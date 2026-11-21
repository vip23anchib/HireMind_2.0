"""
Celery Background Tasks for Asynchronous Resume Processing.
Decouples heavy PDF text extraction, OCR, skill parsing, and ATS score recalculation
from the synchronous HTTP request/response cycle.
"""

import logging
from celery import shared_task
from django.db import transaction

from .models import Document, Application, UserData
from .services.resume_parser import extract_pdf_text, is_valid_resume, extract_metadata_from_text
from .services.skill_service import extract_skills_from_text, sync_candidate_skills
from .services.matching_service import calculate_ats_match
from .services.activity_service import log_activity

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=5)
def process_resume_task(self, document_id, application_id=None):
    """
    Asynchronously parses an uploaded candidate resume document.
    State machine: Uploaded -> Queued -> Processing -> Completed (or Failed)
    """
    try:
        doc = Document.objects.select_related('user_data').get(id=document_id)
    except Document.DoesNotExist:
        logger.error(f"[process_resume_task] Document with id {document_id} does not exist.")
        return {"status": "Error", "message": f"Document {document_id} not found."}

    candidate = doc.user_data

    try:
        # 1. Transition status to Processing
        doc.status = 'Processing'
        doc.save(update_fields=['status'])

        # 2. Extract text from the PDF file
        file_path = doc.file.path
        text = extract_pdf_text(file_path)

        if not text or not is_valid_resume(text):
            logger.warning(f"[process_resume_task] Document {document_id} text is invalid or empty.")
            doc.status = 'Failed'
            doc.save(update_fields=['status'])
            return {
                "status": "Failed",
                "document_id": document_id,
                "message": "Unable to extract readable resume text or invalid format."
            }

        # 3. Extract metadata and update candidate details atomically
        metadata = extract_metadata_from_text(text)
        extracted_skills = extract_skills_from_text(text)

        with transaction.atomic():
            if candidate:
                # Update candidate phone if missing and extracted
                if metadata.get('phone') and not candidate.phone_number:
                    candidate.phone_number = metadata['phone'][:15]
                    candidate.save(update_fields=['phone_number'])

                # Sync candidate skills
                sync_candidate_skills(
                    candidate=candidate,
                    detected_skills=extracted_skills,
                    skill_experience_map=metadata.get('skill_experience', {})
                )

                # 4. Recalculate ATS score for linked applications
                apps_to_update = []
                if application_id:
                    apps_to_update = Application.objects.filter(id=application_id)
                else:
                    apps_to_update = Application.objects.filter(candidate=candidate)

                for app in apps_to_update:
                    match_result = calculate_ats_match(candidate, app.job)
                    score = match_result.get('score', 0.0) if isinstance(match_result, dict) else float(match_result)
                    app.ats_score = score
                    app.save(update_fields=['ats_score'])

                candidate_name = candidate.name
                candidate_id = candidate.id
            else:
                candidate_name = "Unassigned"
                candidate_id = None

            # 5. Mark document as Completed
            doc.status = 'Completed'
            doc.save(update_fields=['status'])

            # 6. Log audit activity
            log_activity(
                action=f"Asynchronously parsed resume for '{candidate_name}' ({len(extracted_skills)} skills indexed)",
                candidate=candidate,
                performed_by=None
            )

        logger.info(f"[process_resume_task] Successfully processed document {document_id} for {candidate_name}")
        return {
            "status": "Completed",
            "document_id": document_id,
            "candidate_id": candidate_id,
            "skills_count": len(extracted_skills),
            "matched_skills": [s if isinstance(s, str) else s.get('name', '') for s in extracted_skills]
        }

    except Exception as exc:
        logger.exception(f"[process_resume_task] Error processing document {document_id}: {exc}")
        # Retry for transient errors
        try:
            doc.status = 'Processing'
            doc.save(update_fields=['status'])
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            doc.status = 'Failed'
            doc.save(update_fields=['status'])
            candidate_label = candidate.name if candidate else f"Doc #{document_id}"
            log_activity(
                action=f"Resume processing failed for '{candidate_label}' after max retries: {str(exc)}",
                candidate=candidate,
                performed_by=None
            )
            return {
                "status": "Failed",
                "document_id": document_id,
                "error": str(exc)
            }

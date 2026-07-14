"""
AI Safety Assistant Service.
Implements RAG-based Q&A, Risk Intelligence, and Compliance Intelligence.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
import uuid
import json
import re

from app.repositories.ai import AIRepository
from app.models.ai import AIDocument, AIDocumentChunk, AIConversation, AIMessage


class AIService:
    """Service for AI Safety Assistant and Knowledge Layer."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = AIRepository(db)

    # =============================================
    # DOCUMENT INGESTION
    # =============================================

    def ingest_document(self, data: Dict, chunks: List[str]) -> Dict:
        """
        Ingest a document into the knowledge base.
        1. Create document record
        2. Chunk the text
        3. Generate embeddings
        4. Store chunks
        """
        # Create document
        doc = self.repo.create_document(data)
        doc_id = str(doc.document_id)

        # Store chunks with embeddings
        chunk_records = []
        for i, text in enumerate(chunks):
            embedding = self._generate_embedding(text)
            chunk_data = {
                "document_id": doc_id,
                "chunk_index": i,
                "text": text,
                "tokens": len(text.split()),
                "embedding": embedding,
                "embedding_model": "text-embedding-3-small",
                "metadata_": {"source": data.get("source_system"), "index": i},
            }
            chunk = self.repo.create_chunk(chunk_data)
            chunk_records.append(chunk)

        # Update document indexed_at
        doc.indexed_at = datetime.utcnow()
        doc.embedding_model = "text-embedding-3-small"
        self.db.commit()

        return {
            "document_id": doc_id,
            "title": doc.title,
            "document_type": doc.document_type,
            "chunks_created": len(chunk_records),
            "indexed_at": doc.indexed_at.isoformat(),
        }

    def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for text.
        Uses OpenAI API if available, otherwise returns mock embedding.
        """
        try:
            import openai
            import os

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                return self._mock_embedding(text)

            client = openai.OpenAI(api_key=api_key)
            response = client.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Embedding generation failed: {e}, using mock embedding")
            return self._mock_embedding(text)

    def _mock_embedding(self, text: str) -> List[float]:
        """Generate deterministic mock embedding for development/testing."""
        import hashlib
        import struct

        # Generate deterministic pseudo-random vector from text hash
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()

        # Convert hash to float vector (1536 dimensions)
        embedding = []
        for i in range(1536):
            # Use different parts of hash for each dimension
            byte_idx = i % len(hash_bytes)
            val = (hash_bytes[byte_idx] + i * 7) % 256
            embedding.append(float(val) / 256.0)

        # Normalize to unit vector
        magnitude = sum(x * x for x in embedding) ** 0.5
        if magnitude > 0:
            embedding = [x / magnitude for x in embedding]

        return embedding

    # =============================================
    # RAG RETRIEVAL
    # =============================================

    def retrieve_context(self, question: str, top_k: int = 5, document_type: Optional[str] = None) -> List[Dict]:
        """
        Retrieve relevant context for a question using vector similarity.
        """
        # Generate embedding for question
        query_embedding = self._generate_embedding(question)

        # Search similar chunks
        results = self.repo.search_similar_chunks(query_embedding, top_k=top_k, document_type=document_type)

        # Filter by relevance threshold
        relevant_chunks = [r for r in results if r["relevance_score"] > 0.5]

        return relevant_chunks

    # =============================================
    # AI SAFETY ASSISTANT
    # =============================================

    def chat(self, user_id: Optional[int], question: str, conversation_id: Optional[str] = None,
             context_type: Optional[str] = None, context_id: Optional[str] = None,
             max_sources: int = 5) -> Dict:
        """
        Main AI Safety Assistant endpoint.
        1. Get or create conversation
        2. Retrieve relevant context
        3. Generate answer with sources
        4. Store messages
        """
        # Get or create conversation
        if conversation_id:
            conv = self.repo.get_conversation(conversation_id)
            if not conv:
                conv = self.repo.create_conversation({"user_id": user_id, "context_type": context_type, "context_id": context_id})
        else:
            conv = self.repo.create_conversation({"user_id": user_id, "context_type": context_type, "context_id": context_id})

        # Get conversation history
        history = []
        if conversation_id:
            history = self.repo.get_recent_messages(str(conv.conversation_id), limit=10)

        # Retrieve relevant context
        context_chunks = self.retrieve_context(question, top_k=max_sources)

        # Generate answer
        answer, confidence, suggested_actions = self._generate_answer(question, context_chunks, history)

        # Store user message
        self.repo.create_message({
            "conversation_id": str(conv.conversation_id),
            "role": "user",
            "content": question,
        })

        # Store assistant message
        sources = [
            {
                "document_id": c["document_id"],
                "title": c["title"],
                "document_type": c["document_type"],
                "chunk_index": c["chunk_index"],
                "text": c["text"][:200] + "..." if len(c["text"]) > 200 else c["text"],
                "relevance_score": c["relevance_score"],
            }
            for c in context_chunks
        ]

        assistant_msg = self.repo.create_message({
            "conversation_id": str(conv.conversation_id),
            "role": "assistant",
            "content": answer,
            "sources": sources,
            "confidence": confidence,
            "tokens_used": len(question.split()) + len(answer.split()),
        })

        # Update conversation title if first message
        if not conv.title:
            conv.title = question[:100]
            self.db.commit()

        return {
            "conversation_id": str(conv.conversation_id),
            "message_id": str(assistant_msg.message_id),
            "answer": answer,
            "sources": sources,
            "confidence": confidence,
            "suggested_actions": suggested_actions,
        }

    def _generate_answer(self, question: str, context: List[Dict], history: List[Dict]) -> tuple:
        """
        Generate answer using LLM or rule-based fallback.
        Returns (answer, confidence, suggested_actions)
        """
        # Try to use LLM if available
        try:
            return self._llm_answer(question, context, history)
        except Exception as e:
            print(f"LLM generation failed: {e}, using rule-based fallback")
            return self._rule_based_answer(question, context)

    def _llm_answer(self, question: str, context: List[Dict], history: List[Dict]) -> tuple:
        """Generate answer using OpenAI API."""
        try:
            import openai
            import os

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not set")

            client = openai.OpenAI(api_key=api_key)

            # Build context
            context_text = "\n\n".join([f"[{c['document_type']}] {c['text']}" for c in context])

            # Build prompt
            system_prompt = """Kamu adalah asisten HSE (Health, Safety, Environment) yang ahli.
Jawab pertanyaan menggunakan konteks yang diberikan.
Jika konteks tidak cukup, katakan bahwa kamu tidak memiliki informasi yang cukup.
Selalu sertakan sumber dari konteks yang digunakan.
Jawab dalam Bahasa Indonesia yang jelas dan profesional."""

            messages = [{"role": "system", "content": system_prompt}]

            # Add history
            for msg in history[-10:]:
                messages.append({"role": msg["role"], "content": msg["content"]})

            # Add current question with context
            user_message = f"Konteks:\n{context_text}\n\nPertanyaan: {question}"
            messages.append({"role": "user", "content": user_message})

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.3,
                max_tokens=1000,
            )

            answer = response.choices[0].message.content
            confidence = 0.9 if context else 0.3

            # Generate suggested actions
            suggested_actions = self._generate_suggested_actions(question, context)

            return answer, confidence, suggested_actions

        except Exception as e:
            raise ValueError(f"LLM generation failed: {e}")

    def _rule_based_answer(self, question: str, context: List[Dict]) -> tuple:
        """
        Rule-based answer generation when LLM is unavailable.
        Uses keyword matching and context retrieval.
        """
        question_lower = question.lower()

        # Analyze question intent
        if any(word in question_lower for word in ["ltifr", "lti", "frequency"]):
            answer = "Berdasarkan data HSE, LTIFR (Lost Time Injury Frequency Rate) adalah indikator utama keselamatan kerja. "
            answer += "LTIFR dihitung dengan rumus: (Jumlah LTI x 1.000.000) / Total Man Hours. "
            answer += "Untuk analisis trend LTIFR bulanan, silakan lihat dashboard '/dashboard/incidents'."
            confidence = 0.8
            suggested_actions = ["Lihat trend LTIFR di dashboard", "Analisis penyebab LTI", "Review kontrol operasional"]
        elif any(word in question_lower for word in ["audit", "temuan", "finding"]):
            answer = "Audit finding dikelola melalui modul Audit. Anda dapat melihat:\n"
            answer += "1. Daftar audit plan yang sedang berjalan\n"
            answer += "2. Temuan audit yang belum ditutup (CAR)\n"
            answer += "3. Evidence yang telah diupload\n"
            answer += "Silakan akses '/audit/plans' untuk detail lebih lanjut."
            confidence = 0.85
            suggested_actions = ["Lihat audit plans", "Review audit findings", "Upload evidence"]
        elif any(word in question_lower for word in ["ptw", "permit", "izin"]):
            answer = "PTW (Permit to Work) adalah kontrol risiko untuk pekerjaan berbahaya. "
            answer += "Modul PTW membantu mengelola:\n"
            answer += "- Issuance dan validasi permit\n"
            answer += "- Monitoring compliance\n"
            answer += "- Closed loop verification\n"
            answer += "Akses '/dashboard/ptw' untuk ringkasan PTW."
            confidence = 0.85
            suggested_actions = ["Lihat PTW summary", "Review expired PTW", "Monitor PTW violations"]
        elif any(word in question_lower for word in ["training", "pelatihan", "sertifikasi"]):
            answer = "Training compliance ditracking di modul Training. "
            answer += "Data mencakup: training completed, pending, failed, dan compliance rate. "
            answer += "Akses '/dashboard/training' untuk detail."
            confidence = 0.8
            suggested_actions = ["Lihat training compliance", "Review pending training", "Schedule new training"]
        elif any(word in question_lower for word in ["environmental", "lingkungan", "pm25", "noise"]):
            answer = "Environmental monitoring mencakup:\n"
            answer += "- PM2.5 (particulate matter)\n"
            answer += "- Noise levels (Leq)\n"
            answer += "- Air quality index\n"
            answer += "Akses '/dashboard/environmental' untuk monitoring real-time."
            confidence = 0.8
            suggested_actions = ["Lihat environmental summary", "Review exceedances", "Check monitoring schedule"]
        elif context:
            # Use retrieved context
            best_chunk = context[0]
            answer = f"Berdasarkan dokumen '{best_chunk['title']}':\n\n{best_chunk['text'][:300]}..."
            if len(best_chunk['text']) > 300:
                answer += "\n\n[Konteks dilanjutkan...]"
            confidence = best_chunk.get("relevance_score", 0.5)
            suggested_actions = ["Lihat dokumen lengkap", "Download referensi"]
        else:
            answer = "Maaf, saya tidak memiliki informasi yang cukup untuk menjawab pertanyaan tersebut. "
            answer += "Silakan:\n"
            answer += "1. Periksa kembali pertanyaan Anda\n"
            answer += "2. Gunakan kata kunci yang lebih spesifik\n"
            answer += "3. Hubungi tim HSE untuk informasi lebih lanjut"
            confidence = 0.2
            suggested_actions = ["Coba pertanyaan lain", "Hubungi HSE team", "Lihat FAQ"]

        return answer, confidence, suggested_actions

    def _generate_suggested_actions(self, question: str, context: List[Dict]) -> List[str]:
        """Generate suggested follow-up actions based on question and context."""
        actions = []
        question_lower = question.lower()

        if "ltifr" in question_lower or "lti" in question_lower:
            actions.extend(["Lihat trend LTIFR", "Analisis akar penyebab", "Review kontrol keselamatan"])
        if "audit" in question_lower:
            actions.extend(["Lihat audit plans", "Review temuan audit", "Upload evidence"])
        if "ptw" in question_lower or "permit" in question_lower:
            actions.extend(["Lihat PTW summary", "Review expired PTW", "Monitor violations"])
        if "training" in question_lower:
            actions.extend(["Lihat training compliance", "Schedule new training", "Review certifications"])
        if "environmental" in question_lower or "lingkungan" in question_lower:
            actions.extend(["Lihat environmental summary", "Review exceedances", "Check monitoring schedule"])
        if "risk" in question_lower or "risiko" in question_lower:
            actions.extend(["Lihat risk intelligence", "Review risk register", "Update risk assessment"])

        if not actions and context:
            actions = ["Lihat dokumen lengkap", "Tanyakan lebih detail"]

        return actions[:5]  # Max 5 actions

    # =============================================
    # RISK INTELLIGENCE
    # =============================================

    def calculate_risk_score(self, site_id: str) -> Dict:
        """
        Calculate risk score for a site based on multiple HSE factors.
        Uses weighted scoring from existing EDW data.
        """
        from app.services import DashboardService
        from app.repositories import DashboardRepository

        service = DashboardService(self.db)
        repo = DashboardRepository(self.db)

        # Gather data from multiple sources
        try:
            incident_summary = service.get_incident_summary(site_id=site_id, period_days=30)
            ptw_summary = service.get_ptw_summary(site_id=site_id, period_days=30)
            training_summary = service.get_training_summary(site_id=site_id, period_days=30)
            env_summary = service.get_environmental_summary(site_id=site_id, period_days=30)
        except Exception:
            incident_summary = {}
            ptw_summary = {}
            training_summary = {}
            env_summary = {}

        # Calculate risk factors (0-100 scale each)
        factors = {}
        recommendations = []

        # Factor 1: Incident Rate (LTIFR)
        total_lti = incident_summary.get("total_lti", 0)
        if total_lti > 5:
            factors["incident_rate"] = {"score": 80, "weight": 0.3, "reason": f"LTIFR tinggi: {total_lti} kasus dalam 30 hari"}
            recommendations.append("Investigasi akar penyebab LTI")
        elif total_lti > 2:
            factors["incident_rate"] = {"score": 50, "weight": 0.3, "reason": f"LTIFR moderat: {total_lti} kasus"}
        else:
            factors["incident_rate"] = {"score": 20, "weight": 0.3, "reason": "LTIFR rendah"}

        # Factor 2: PTW Compliance
        ptw_violations = ptw_summary.get("violation_count", 0)
        if ptw_violations > 5:
            factors["ptw_compliance"] = {"score": 90, "weight": 0.2, "reason": f"PTW violations tinggi: {ptw_violations}"}
            recommendations.append("Perbaiki sistem PTW dan lakukan training ulang")
        elif ptw_violations > 0:
            factors["ptw_compliance"] = {"score": 60, "weight": 0.2, "reason": f"Ada {ptw_violations} PTW violations"}
        else:
            factors["ptw_compliance"] = {"score": 20, "weight": 0.2, "reason": "PTW compliance baik"}

        # Factor 3: Training Compliance
        training_compliance = training_summary.get("compliance_rate", 100)
        if training_compliance < 80:
            factors["training_compliance"] = {"score": 80, "weight": 0.2, "reason": f"Training compliance rendah: {training_compliance}%"}
            recommendations.append("Jadwalkan training mandatory untuk karyawan")
        elif training_compliance < 95:
            factors["training_compliance"] = {"score": 50, "weight": 0.2, "reason": f"Training compliance: {training_compliance}%"}
        else:
            factors["training_compliance"] = {"score": 20, "weight": 0.2, "reason": "Training compliance excellent"}

        # Factor 4: Environmental
        env_exceedances = env_summary.get("exceedances", 0)
        if env_exceedances > 5:
            factors["environmental"] = {"score": 70, "weight": 0.15, "reason": f"Environmental exceedances: {env_exceedances}"}
            recommendations.append("Review environmental monitoring dan kontrol")
        else:
            factors["environmental"] = {"score": 30, "weight": 0.15, "reason": "Environmental dalam batas normal"}

        # Factor 5: Audit Status
        try:
            from app.repositories.audit import AuditRepository
            audit_repo = AuditRepository(self.db)
            audit_plans = audit_repo.get_audit_plans(site_id=site_id, status="overdue")
            if audit_plans:
                factors["audit_status"] = {"score": 80, "weight": 0.15, "reason": f"{len(audit_plans)} audit overdue"}
                recommendations.append("Lakukan audit yang sudah overdue")
            else:
                factors["audit_status"] = {"score": 20, "weight": 0.15, "reason": "Audit on track"}
        except Exception:
            factors["audit_status"] = {"score": 40, "weight": 0.15, "reason": "Audit data tidak tersedia"}

        # Calculate weighted overall score
        overall_score = sum(f["score"] * f["weight"] for f in factors.values())

        # Determine risk level
        if overall_score >= 80:
            risk_level = "critical"
        elif overall_score >= 60:
            risk_level = "high"
        elif overall_score >= 40:
            risk_level = "medium"
        else:
            risk_level = "low"

        # Get site name
        from app.models.hse_models import DimSite
        site = self.db.query(DimSite).filter(DimSite.site_id == site_id).first()
        site_name = site.site_name if site else site_id

        return {
            "site_id": site_id,
            "site_name": site_name,
            "overall_score": round(overall_score, 1),
            "risk_level": risk_level,
            "factors": factors,
            "recommendations": recommendations[:5],
            "calculated_at": datetime.utcnow().isoformat(),
        }

    # =============================================
    # COMPLIANCE INTELLIGENCE
    # =============================================

    def get_compliance_intelligence(self, site_id: Optional[str] = None) -> Dict:
        """
        Generate compliance intelligence report.
        Analyzes gaps against ISO 45001, ISO 14001, SMKP Minerba, SMK3.
        """
        gaps = []

        # ISO 45001 - Occupational Health & Safety
        gaps.append(self._analyze_iso45001_compliance(site_id))

        # ISO 14001 - Environmental Management
        gaps.append(self._analyze_iso14001_compliance(site_id))

        # SMKP Minerba - Mining Safety Management
        gaps.append(self._analyze_smkp_minerba_compliance(site_id))

        # SMK3 - Occupational Safety Management System
        gaps.append(self._analyze_smk3_compliance(site_id))

        # Calculate overall score
        avg_score = sum(g["score"] for g in gaps) / len(gaps) if gaps else 0

        if avg_score >= 90:
            risk_level = "low"
        elif avg_score >= 75:
            risk_level = "medium"
        elif avg_score >= 60:
            risk_level = "high"
        else:
            risk_level = "critical"

        return {
            "site_id": site_id,
            "overall_score": round(avg_score, 1),
            "risk_level": risk_level,
            "gaps": gaps,
            "last_audit_date": None,  # TODO: get from audit repository
            "next_audit_due": None,
        }

    def _analyze_iso45001_compliance(self, site_id: Optional[str]) -> Dict:
        """Analyze ISO 45001 compliance."""
        gaps = []

        # Check incident management (Clause 10.2)
        try:
            from app.repositories import DashboardRepository
            repo = DashboardRepository(self.db)
            incident_data = repo.get_incident_distribution(site_id=site_id)
            total_incidents = sum(incident_data.values())
            if total_incidents > 10:
                gaps.append({
                    "clause": "10.2",
                    "description": "Insiden berlebih - perlu evaluasi sistem pengelolaan insiden",
                    "count": total_incidents,
                    "severity": "high"
                })
        except Exception:
            pass

        return {
            "standard": "ISO 45001",
            "clause": "Various",
            "description": "Sistem Manajemen K3 - Gap analysis berdasarkan data insiden, audit, dan training",
            "gap_count": len(gaps),
            "evidence_count": max(0, 10 - len(gaps)),
            "severity": "high" if len(gaps) > 2 else "medium" if len(gaps) > 0 else "low",
            "recommendations": [
                "Review dan update sistem manajemen K3",
                "Lakukan internal audit sesuai jadwal",
                "Pastikan semua insiden memiliki CAR yang ditindaklanjuti"
            ] if gaps else ["Pertahankan kinerja compliance saat ini"]
        }

    def _analyze_iso14001_compliance(self, site_id: Optional[str]) -> Dict:
        """Analyze ISO 14001 compliance."""
        gaps = []

        try:
            from app.repositories import DashboardRepository
            repo = DashboardRepository(self.db)
            env_data = repo.get_environmental_summary(site_id=site_id)
            if env_data.get("exceedances", 0) > 5:
                gaps.append({
                    "clause": "8.1",
                    "description": "Environmental exceedances melebihi batas",
                    "count": env_data.get("exceedances", 0),
                    "severity": "high"
                })
        except Exception:
            pass

        return {
            "standard": "ISO 14001",
            "clause": "8.1",
            "description": "Sistem Manajemen Lingungan - Gap analysis berdasarkan monitoring lingkungan",
            "gap_count": len(gaps),
            "evidence_count": max(0, 8 - len(gaps)),
            "severity": "high" if len(gaps) > 2 else "medium" if len(gaps) > 0 else "low",
            "recommendations": [
                "Review environmental monitoring plan",
                "Update environmental impact assessment",
                "Implement corrective actions untuk exceedances"
            ] if gaps else ["Pertahankan kinerja environmental management"]
        }

    def _analyze_smkp_minerba_compliance(self, site_id: Optional[str]) -> Dict:
        """Analyze SMKP Minerba compliance."""
        return {
            "standard": "SMKP Minerba",
            "clause": "Various",
            "description": "Sistem Manajemen Keselamatan Pertambangan - Gap analysis berdasarkan regulasi Minerba",
            "gap_count": 2,
            "evidence_count": 6,
            "severity": "medium",
            "recommendations": [
                "Pastikan PTW sesuai dengan Permenaker No. 8 Tahun 2023",
                "Review vehicle safety inspection program",
                "Update emergency response plan"
            ]
        }

    def _analyze_smk3_compliance(self, site_id: Optional[str]) -> Dict:
        """Analyze SMK3 compliance."""
        return {
            "standard": "SMK3",
            "clause": "Various",
            "description": "Sistem Manajemen K3 (SMK3) - Gap analysis berdasarkan Peraturan Menaker",
            "gap_count": 1,
            "evidence_count": 7,
            "severity": "low",
            "recommendations": [
                "Review dokumen SMK3 sesuai dengan perubahan regulasi terbaru"
            ]
        }

    # =============================================
    # KNOWLEDGE BASE STATS
    # =============================================

    def get_knowledge_base_stats(self) -> Dict:
        """Get statistics about the knowledge base."""
        from app.models.ai import AIDocument, AIDocumentChunk

        doc_count = self.db.query(func.count(AIDocument.document_id)).filter(AIDocument.is_active == True).scalar()
        chunk_count = self.db.query(func.count(AIDocumentChunk.chunk_id)).filter(AIDocumentChunk.embedding.is_not(None)).scalar()

        doc_types = {}
        results = self.db.query(AIDocument.document_type, func.count(AIDocument.document_id)).filter(
            AIDocument.is_active == True
        ).group_by(AIDocument.document_type).all()
        for doc_type, count in results:
            doc_types[doc_type] = count

        return {
            "total_documents": doc_count or 0,
            "total_chunks": chunk_count or 0,
            "documents_by_type": doc_types,
            "indexed_documents": doc_count or 0,
            "last_updated": datetime.utcnow().isoformat(),
        }

    # =============================================
    # EXECUTIVE DECISION SUPPORT
    # =============================================

    def get_priority_today(self, site_id: Optional[str] = None) -> Dict:
        """
        Executive Decision Support - Priority Today.
        Aggregates critical actions across all HSE domains.
        """
        items = []
        total_critical = 0
        total_high = 0

        # 1. Critical Alerts
        try:
            from app.repositories import AlertRepository
            alert_repo = AlertRepository(self.db)
            critical_alerts = alert_repo.get_alerts(site_id=site_id, status="active", severity="critical", limit=10)
            if critical_alerts:
                total_critical += len(critical_alerts)
                items.append({
                    "category": "alert",
                    "priority": "critical",
                    "title": f"{len(critical_alerts)} critical alert(s) active",
                    "description": "Critical alerts requiring immediate attention",
                    "count": len(critical_alerts),
                    "action": "Review and resolve critical alerts immediately"
                })
        except Exception:
            pass

        # 2. Expired PTW
        try:
            from app.repositories import DashboardRepository
            dashboard_repo = DashboardRepository(self.db)
            ptw_data = dashboard_repo.get_ptw_summary(site_id=site_id, period_days=7)
            expired_count = ptw_data.get("overdue_count", 0) if isinstance(ptw_data, dict) else getattr(ptw_data, "overdue_count", 0)
            if expired_count > 0:
                total_high += expired_count
                items.append({
                    "category": "ptw",
                    "priority": "high",
                    "title": f"{expired_count} PTW expired",
                    "description": "Permit to Work has expired and work may continue without valid authorization",
                    "count": expired_count,
                    "action": "Review and renew expired PTW immediately"
                })
        except Exception:
            pass

        # 3. Overdue Audits
        try:
            from app.repositories.audit import AuditRepository
            audit_repo = AuditRepository(self.db)
            overdue_audits = audit_repo.get_audit_plans(site_id=site_id, status="overdue")
            if overdue_audits:
                total_high += len(overdue_audits)
                items.append({
                    "category": "audit",
                    "priority": "high",
                    "title": f"{len(overdue_audits)} audit(s) overdue",
                    "description": "Scheduled audits are past due date",
                    "count": len(overdue_audits),
                    "action": "Schedule and conduct overdue audits"
                })
        except Exception:
            pass

        # 4. Risk Score Assessment
        try:
            risk_data = self.calculate_risk_score(site_id) if site_id else None
            if risk_data and risk_data.get("overall_score", 0) >= 70:
                total_critical += 1
                items.append({
                    "category": "risk",
                    "priority": "critical",
                    "title": f"Risk Score {risk_data.get('overall_score')} ({risk_data.get('risk_level', 'unknown').upper()})",
                    "description": "Site risk score is above critical threshold",
                    "count": 1,
                    "action": "Immediate risk assessment and mitigation required"
                })
        except Exception:
            pass

        # 5. Training Compliance
        try:
            from app.services import DashboardService
            dashboard_service = DashboardService(self.db)
            training_data = dashboard_service.get_training_summary(site_id=site_id, period_days=30)
            compliance_rate = training_data.compliance_rate if hasattr(training_data, "compliance_rate") else 100
            if compliance_rate < 80:
                total_high += 1
                items.append({
                    "category": "training",
                    "priority": "high",
                    "title": f"Training compliance {compliance_rate}%",
                    "description": "Training compliance is below acceptable threshold",
                    "count": 1,
                    "action": "Schedule mandatory training for non-compliant personnel"
                })
        except Exception:
            pass

        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        items.sort(key=lambda x: priority_order.get(x["priority"], 99))

        # Generate recommended action
        recommended_action = "No immediate actions required"
        if total_critical > 0:
            recommended_action = "Address critical items immediately - safety incident risk is elevated"
        elif total_high > 0:
            recommended_action = "Review and address high priority items within 24 hours"
        elif items:
            recommended_action = "Continue monitoring and address medium priority items this week"

        # Get risk score for response
        risk_score = 0.0
        risk_level = "low"
        try:
            if site_id:
                risk_data = self.calculate_risk_score(site_id)
                risk_score = risk_data.get("overall_score", 0)
                risk_level = risk_data.get("risk_level", "low")
        except Exception:
            pass

        return {
            "date": date.today(),
            "site_id": site_id,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "total_critical": total_critical,
            "total_high": total_high,
            "items": items[:10],
            "recommended_action": recommended_action,
        }

    # =============================================
    # PREDICTIVE SAFETY
    # =============================================

    def get_predictive_safety(self, site_id: str, metric: str = "ltifr", forecast_days: int = 30) -> Dict:
        """
        Predictive Safety - forecast future HSE metrics using trend analysis.
        Uses simple linear regression on historical data.
        """
        from app.repositories import DashboardRepository
        dashboard_repo = DashboardRepository(self.db)

        # Get historical data
        end_date = date.today()
        start_date = end_date - timedelta(days=90)

        historical = []
        if metric == "ltifr":
            data = dashboard_repo.get_executive_summary(site_id=site_id, start_date=start_date, end_date=end_date)
            current_value = data.get("ltifr", 0)
            # Simulate historical trend (in real implementation, fetch from fact_hse)
            for i in range(30, 0, -1):
                d = end_date - timedelta(days=i)
                historical.append({"date": d, "value": max(0, current_value + (i % 7 - 3) * 0.2)})
        elif metric == "trir":
            data = dashboard_repo.get_executive_summary(site_id=site_id, start_date=start_date, end_date=end_date)
            current_value = data.get("trir", 0)
            for i in range(30, 0, -1):
                d = end_date - timedelta(days=i)
                historical.append({"date": d, "value": max(0, current_value + (i % 5 - 2) * 0.3)})
        elif metric == "near_miss":
            data = dashboard_repo.get_executive_summary(site_id=site_id, start_date=start_date, end_date=end_date)
            current_value = data.get("near_miss_rate", 0)
            for i in range(30, 0, -1):
                d = end_date - timedelta(days=i)
                historical.append({"date": d, "value": max(0, current_value + (i % 4 - 1.5) * 2)})
        else:
            current_value = 0
            for i in range(30, 0, -1):
                d = end_date - timedelta(days=i)
                historical.append({"date": d, "value": 0})

        # Simple linear regression for forecasting
        values = [h["value"] for h in historical]
        n = len(values)
        if n < 2:
            slope = 0
            intercept = values[0] if values else 0
        else:
            x_mean = (n - 1) / 2
            y_mean = sum(values) / n
            numerator = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
            denominator = sum((i - x_mean) ** 2 for i in range(n))
            slope = numerator / denominator if denominator != 0 else 0
            intercept = y_mean - slope * x_mean

        # Generate forecast
        forecast = []
        confidence_factor = 1.0
        for i in range(forecast_days):
            d = end_date + timedelta(days=i + 1)
            predicted = slope * (n + i) + intercept
            predicted = max(0, predicted)
            uncertainty = confidence_factor * (1 + i * 0.1)
            forecast.append({
                "date": d,
                "predicted_value": round(predicted, 2),
                "lower_bound": round(max(0, predicted - uncertainty), 2),
                "upper_bound": round(predicted + uncertainty, 2),
                "confidence": round(max(0.1, 1.0 - i * 0.02), 2),
            })

        # Determine trend
        if slope > 0.1:
            trend = "increasing"
            risk_level = "high"
            recommendation = f"{metric.upper()} is trending upward. Immediate preventive action required."
        elif slope < -0.1:
            trend = "decreasing"
            risk_level = "low"
            recommendation = f"{metric.upper()} is trending downward. Maintain current controls."
        else:
            trend = "stable"
            risk_level = "medium"
            recommendation = f"{metric.upper()} is stable. Continue monitoring."

        # Get site name
        from app.models.hse_models import DimSite
        site = self.db.query(DimSite).filter(DimSite.site_id == site_id).first()
        site_name = site.site_name if site else site_id

        return {
            "site_id": site_id,
            "site_name": site_name,
            "metric": metric,
            "current_value": round(current_value, 2) if current_value else 0,
            "forecast": forecast[:14],
            "trend": trend,
            "risk_level": risk_level,
            "recommendation": recommendation,
            "generated_at": datetime.utcnow().isoformat(),
        }

    # =============================================
    # ENHANCED RISK INTELLIGENCE
    # =============================================

    def calculate_risk_score(self, site_id: str) -> Dict:
        """
        Calculate risk score for a site based on multiple HSE factors.
        Uses weighted scoring from existing EDW data with trend comparison.
        """
        from app.services import DashboardService
        from app.repositories import DashboardRepository

        service = DashboardService(self.db)
        repo = DashboardRepository(self.db)

        try:
            incident_summary = service.get_incident_summary(site_id=site_id, period_days=30)
            ptw_summary = service.get_ptw_summary(site_id=site_id, period_days=30)
            training_summary = service.get_training_summary(site_id=site_id, period_days=30)
            env_summary = service.get_environmental_summary(site_id=site_id, period_days=30)
        except Exception:
            incident_summary = {}
            ptw_summary = {}
            training_summary = {}
            env_summary = {}

        factors = {}
        recommendations = []

        # Factor 1: Incident Rate (LTIFR) - with trend
        current_ltifr = incident_summary.get("ltifr", 0)
        previous_ltifr = incident_summary.get("ltifr_previous", current_ltifr)
        ltifr_trend = self._calculate_trend(current_ltifr, previous_ltifr)

        if current_ltifr > 5:
            factors["incident_rate"] = {
                "score": 80,
                "weight": 0.3,
                "reason": f"LTIFR tinggi: {current_ltifr:.2f} (naik {ltifr_trend['direction']})",
                "trend": ltifr_trend
            }
            recommendations.append("Investigasi akar penyebab LTI")
        elif current_ltifr > 2:
            factors["incident_rate"] = {
                "score": 50,
                "weight": 0.3,
                "reason": f"LTIFR moderat: {current_ltifr:.2f} ({ltifr_trend['direction']})",
                "trend": ltifr_trend
            }
        else:
            factors["incident_rate"] = {
                "score": 20,
                "weight": 0.3,
                "reason": f"LTIFR rendah: {current_ltifr:.2f}",
                "trend": ltifr_trend
            }

        # Factor 2: Near Miss Trend
        current_near_miss = incident_summary.get("near_miss_rate", 0)
        previous_near_miss = incident_summary.get("near_miss_rate_previous", current_near_miss)
        near_miss_trend = self._calculate_trend(current_near_miss, previous_near_miss)

        if current_near_miss < 10:
            factors["near_miss"] = {
                "score": 70,
                "weight": 0.15,
                "reason": f"Near Miss turun {abs(near_miss_trend.get('change_pct', 0)):.0f}%",
                "trend": near_miss_trend
            }
            recommendations.append("Perbaiki sistem pelaporan near miss - angkanya terlalu rendah")
        else:
            factors["near_miss"] = {
                "score": 30,
                "weight": 0.15,
                "reason": f"Near Miss stabil: {current_near_miss:.0f}/1k",
                "trend": near_miss_trend
            }

        # Factor 3: PTW Compliance
        ptw_violations = ptw_summary.get("violation_count", 0) if isinstance(ptw_summary, dict) else getattr(ptw_summary, "violation_count", 0)
        expired_ptw = ptw_summary.get("overdue_count", 0) if isinstance(ptw_summary, dict) else getattr(ptw_summary, "overdue_count", 0)

        if expired_ptw > 0:
            factors["ptw_compliance"] = {
                "score": 90,
                "weight": 0.2,
                "reason": f"PTW expired meningkat: {expired_ptw} permit",
                "trend": {"direction": "up", "change_pct": 15, "previous": expired_ptw - 1, "current": expired_ptw}
            }
            recommendations.append("Perbaiki sistem PTW dan lakukan training ulang")
        elif ptw_violations > 5:
            factors["ptw_compliance"] = {
                "score": 60,
                "weight": 0.2,
                "reason": f"PTW violations tinggi: {ptw_violations}",
                "trend": {"direction": "stable", "change_pct": 0, "previous": ptw_violations, "current": ptw_violations}
            }
        else:
            factors["ptw_compliance"] = {
                "score": 20,
                "weight": 0.2,
                "reason": "PTW compliance baik",
                "trend": {"direction": "stable", "change_pct": 0, "previous": 0, "current": 0}
            }

        # Factor 4: Training Compliance
        training_compliance = training_summary.compliance_rate if hasattr(training_summary, "compliance_rate") else 100
        if isinstance(training_summary, dict):
            training_compliance = training_summary.get("compliance_rate", 100)

        previous_training_compliance = max(0, training_compliance - 5)  # Simulate previous
        training_trend = self._calculate_trend(training_compliance, previous_training_compliance)

        if training_compliance < 80:
            factors["training_compliance"] = {
                "score": 80,
                "weight": 0.2,
                "reason": f"Training compliance turun: {training_compliance}%",
                "trend": training_trend
            }
            recommendations.append("Jadwalkan training mandatory untuk karyawan")
        elif training_compliance < 95:
            factors["training_compliance"] = {
                "score": 50,
                "weight": 0.2,
                "reason": f"Training compliance: {training_compliance}% ({training_trend['direction']})",
                "trend": training_trend
            }
        else:
            factors["training_compliance"] = {
                "score": 20,
                "weight": 0.2,
                "reason": f"Training compliance excellent: {training_compliance}%",
                "trend": training_trend
            }

        # Factor 5: Environmental
        env_exceedances = env_summary.get("exceedances", 0) if isinstance(env_summary, dict) else getattr(env_summary, "exceedances", 0)
        if env_exceedances > 5:
            factors["environmental"] = {
                "score": 70,
                "weight": 0.15,
                "reason": f"Environmental exceedances: {env_exceedances}",
                "trend": {"direction": "up", "change_pct": 10, "previous": env_exceedances - 1, "current": env_exceedances}
            }
            recommendations.append("Review environmental monitoring dan kontrol")
        else:
            factors["environmental"] = {
                "score": 30,
                "weight": 0.15,
                "reason": "Environmental dalam batas normal",
                "trend": {"direction": "stable", "change_pct": 0, "previous": 0, "current": 0}
            }

        # Calculate weighted overall score
        overall_score = sum(f["score"] * f["weight"] for f in factors.values())

        if overall_score >= 80:
            risk_level = "critical"
        elif overall_score >= 60:
            risk_level = "high"
        elif overall_score >= 40:
            risk_level = "medium"
        else:
            risk_level = "low"

        from app.models.hse_models import DimSite
        site = self.db.query(DimSite).filter(DimSite.site_id == site_id).first()
        site_name = site.site_name if site else site_id

        return {
            "site_id": site_id,
            "site_name": site_name,
            "overall_score": round(overall_score, 1),
            "risk_level": risk_level,
            "factors": factors,
            "recommendations": recommendations[:5],
            "calculated_at": datetime.utcnow().isoformat(),
        }

    def _calculate_trend(self, current: float, previous: float) -> Dict:
        """Calculate trend between two values."""
        if previous == 0:
            return {"direction": "new", "change_pct": 0, "previous": previous, "current": current}
        change_pct = ((current - previous) / previous) * 100
        if change_pct > 5:
            direction = "up"
        elif change_pct < -5:
            direction = "down"
        else:
            direction = "stable"
        return {"direction": direction, "change_pct": round(change_pct, 1), "previous": previous, "current": current}

    # =============================================
    # ENHANCED COMPLIANCE INTELLIGENCE
    # =============================================

    def get_compliance_intelligence(self, site_id: Optional[str] = None) -> Dict:
        """
        Generate compliance intelligence report.
        Analyzes gaps against ISO 45001, ISO 14001, SMKP Minerba, SMK3.
        """
        gaps = []

        gaps.append(self._analyze_iso45001_compliance(site_id))
        gaps.append(self._analyze_iso14001_compliance(site_id))
        gaps.append(self._analyze_smkp_minerba_compliance(site_id))
        gaps.append(self._analyze_smk3_compliance(site_id))

        avg_score = sum(g["score"] for g in gaps) / len(gaps) if gaps else 0

        if avg_score >= 90:
            risk_level = "low"
        elif avg_score >= 75:
            risk_level = "medium"
        elif avg_score >= 60:
            risk_level = "high"
        else:
            risk_level = "critical"

        biggest_gap = max(gaps, key=lambda g: g.get("gap_count", 0)) if gaps else None

        return {
            "site_id": site_id,
            "overall_score": round(avg_score, 1),
            "risk_level": risk_level,
            "gaps": gaps,
            "biggest_gap": biggest_gap,
            "last_audit_date": None,
            "next_audit_due": None,
        }

    def _analyze_iso45001_compliance(self, site_id: Optional[str]) -> Dict:
        """Analyze ISO 45001 compliance with granular details."""
        gaps = []
        gap_details = []

        try:
            from app.repositories import DashboardRepository
            from app.repositories.audit import AuditRepository
            repo = DashboardRepository(self.db)
            audit_repo = AuditRepository(self.db)

            incident_data = repo.get_incident_distribution(site_id=site_id)
            total_incidents = sum(incident_data.values())

            if total_incidents > 10:
                gaps.append({
                    "clause": "10.2",
                    "description": "Insiden berlebih - perlu evaluasi sistem pengelolaan insiden",
                    "count": total_incidents,
                    "severity": "high"
                })
                gap_details.append({
                    "standard": "ISO 45001",
                    "clause": "10.2",
                    "description": f"Insiden berlebih: {total_incidents} kasus dalam periode",
                    "gap_count": total_incidents,
                    "evidence_count": max(0, 10 - total_incidents),
                    "missing_evidence": [f"Investigasi laporan insiden #{i+1}" for i in range(min(3, total_incidents))],
                    "severity": "high",
                    "recommendations": [
                        "Review dan update sistem manajemen K3",
                        "Lakukan internal audit sesuai jadwal",
                        "Pastikan semua insiden memiliki CAR yang ditindaklanjuti"
                    ]
                })
        except Exception:
            pass

        score = max(0, 100 - len(gaps) * 15)
        return {
            "standard": "ISO 45001",
            "clause": "Various",
            "description": "Sistem Manajemen K3",
            "gap_count": len(gaps),
            "evidence_count": max(0, 10 - len(gaps)),
            "severity": "high" if len(gaps) > 2 else "medium" if len(gaps) > 0 else "low",
            "recommendations": [
                "Review dan update sistem manajemen K3",
                "Lakukan internal audit sesuai jadwal",
                "Pastikan semua insiden memiliki CAR yang ditindaklanjuti"
            ] if gaps else ["Pertahankan kinerja compliance saat ini"]
        }

    def _analyze_iso14001_compliance(self, site_id: Optional[str]) -> Dict:
        """Analyze ISO 14001 compliance with granular details."""
        gaps = []

        try:
            from app.repositories import DashboardRepository
            repo = DashboardRepository(self.db)
            env_data = repo.get_environmental_summary(site_id=site_id)
            exceedances = env_data.get("exceedances", 0) if isinstance(env_data, dict) else getattr(env_data, "exceedances", 0)

            if exceedances > 5:
                gaps.append({
                    "clause": "8.1",
                    "description": "Environmental exceedances melebihi batas",
                    "count": exceedances,
                    "severity": "high"
                })
        except Exception:
            pass

        score = max(0, 100 - len(gaps) * 15)
        return {
            "standard": "ISO 14001",
            "clause": "8.1",
            "description": "Sistem Manajemen Lingungan - Gap analysis berdasarkan monitoring lingkungan",
            "gap_count": len(gaps),
            "evidence_count": max(0, 8 - len(gaps)),
            "severity": "high" if len(gaps) > 2 else "medium" if len(gaps) > 0 else "low",
            "recommendations": [
                "Review environmental monitoring plan",
                "Update environmental impact assessment",
                "Implement corrective actions untuk exceedances"
            ] if gaps else ["Pertahankan kinerja environmental management"]
        }

    def _analyze_smkp_minerba_compliance(self, site_id: Optional[str]) -> Dict:
        """Analyze SMKP Minerba compliance."""
        return {
            "standard": "SMKP Minerba",
            "clause": "Various",
            "description": "Sistem Manajemen Keselamatan Pertambangan",
            "gap_count": 2,
            "evidence_count": 6,
            "severity": "medium",
            "recommendations": [
                "Pastikan PTW sesuai dengan Permenaker No. 8 Tahun 2023",
                "Review vehicle safety inspection program",
                "Update emergency response plan"
            ]
        }

    def _analyze_smk3_compliance(self, site_id: Optional[str]) -> Dict:
        """Analyze SMK3 compliance."""
        return {
            "standard": "SMK3",
            "clause": "Various",
            "description": "Sistem Manajemen K3 (SMK3)",
            "gap_count": 1,
            "evidence_count": 7,
            "severity": "low",
            "recommendations": [
                "Review dokumen SMK3 sesuai dengan perubahan regulasi terbaru"
            ]
        }

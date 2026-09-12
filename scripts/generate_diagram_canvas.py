#!/usr/bin/env python3
"""Generate a complete 6-frame Excalidraw canvas representing all agyFlow architectural points."""

import json
from pathlib import Path
import xml.etree.ElementTree as ET

OUT_DIR = Path(__file__).resolve().parents[1] / "docs/diagrams"
OUT_DIR.mkdir(parents=True, exist_ok=True)

class ExcalidrawBuilder:
    def __init__(self):
        self.elements = []
        self.element_counter = 1000

    def next_id(self):
        self.element_counter += 1
        return f"agy-{self.element_counter}"

    def add_frame(self, name: str, x: float, y: float, w: float, h: float) -> str:
        fid = self.next_id()
        self.elements.append({
            "id": fid,
            "type": "frame",
            "x": x, "y": y, "width": w, "height": h,
            "angle": 0,
            "strokeColor": "#D4DEE4",
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 1.5,
            "strokeStyle": "solid",
            "roughness": 0,
            "opacity": 100,
            "groupIds": [],
            "frameId": None,
            "roundness": None,
            "seed": self.element_counter,
            "version": 1,
            "versionNonce": self.element_counter + 1000,
            "isDeleted": False,
            "boundElements": [],
            "updated": 1789200000000,
            "created": 1789200000000,
            "link": None,
            "locked": False,
            "name": name
        })
        return fid

    def add_rect(self, x: float, y: float, w: float, h: float,
                 stroke: str = "#CFD9E0", bg: str = "#FFFFFF",
                 stroke_width: float = 1.5, stroke_style: str = "solid",
                 roundness: int = 3, frame_id: str = None) -> str:
        rid = self.next_id()
        self.elements.append({
            "id": rid,
            "type": "rectangle",
            "x": x, "y": y, "width": w, "height": h,
            "angle": 0,
            "strokeColor": stroke,
            "backgroundColor": bg,
            "fillStyle": "solid",
            "strokeWidth": stroke_width,
            "strokeStyle": stroke_style,
            "roughness": 0,
            "opacity": 100,
            "groupIds": [],
            "frameId": frame_id,
            "roundness": {"type": roundness} if roundness else None,
            "seed": self.element_counter,
            "version": 1,
            "versionNonce": self.element_counter + 1000,
            "isDeleted": False,
            "boundElements": [],
            "updated": 1789200000000,
            "created": 1789200000000,
            "link": None,
            "locked": False
        })
        return rid

    def add_text(self, text: str, x: float, y: float, w: float = 300,
                 size: int = 16, color: str = "#172D3E",
                 align: str = "left", frame_id: str = None) -> str:
        tid = self.next_id()
        line_count = text.count("\n") + 1
        h = line_count * (size * 1.35)
        self.elements.append({
            "id": tid,
            "type": "text",
            "x": x, "y": y, "width": w, "height": h,
            "angle": 0,
            "strokeColor": color,
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 1,
            "strokeStyle": "solid",
            "roughness": 0,
            "opacity": 100,
            "groupIds": [],
            "frameId": frame_id,
            "roundness": None,
            "seed": self.element_counter,
            "version": 1,
            "versionNonce": self.element_counter + 1000,
            "isDeleted": False,
            "boundElements": [],
            "updated": 1789200000000,
            "created": 1789200000000,
            "link": None,
            "locked": False,
            "text": text,
            "originalText": text,
            "fontSize": size,
            "fontFamily": 2,
            "lineHeight": 1.35,
            "baseline": size,
            "textAlign": align,
            "verticalAlign": "top",
            "containerId": None,
            "autoResize": False
        })
        return tid

    def add_arrow(self, x1: float, y1: float, x2: float, y2: float,
                  color: str = "#8195A3", frame_id: str = None) -> str:
        aid = self.next_id()
        dx = x2 - x1
        dy = y2 - y1
        self.elements.append({
            "id": aid,
            "type": "arrow",
            "x": x1, "y": y1, "width": abs(dx), "height": abs(dy),
            "angle": 0,
            "strokeColor": color,
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 2,
            "strokeStyle": "solid",
            "roughness": 0,
            "opacity": 100,
            "groupIds": [],
            "frameId": frame_id,
            "roundness": None,
            "seed": self.element_counter,
            "version": 1,
            "versionNonce": self.element_counter + 1000,
            "isDeleted": False,
            "boundElements": [],
            "updated": 1789200000000,
            "created": 1789200000000,
            "link": None,
            "locked": False,
            "points": [[0, 0], [dx, dy]],
            "lastCommittedPoint": None,
            "startBinding": None,
            "endBinding": None,
            "startArrowhead": None,
            "endArrowhead": "arrow",
            "elbowed": False
        })
        return aid

    def add_card(self, x: float, y: float, w: float, h: float,
                 title: str, body: str,
                 stroke: str = "#CFD9E0", bg: str = "#FFFFFF",
                 badge: str = None, badge_bg: str = "#E0E0E0", badge_color: str = "#333333",
                 frame_id: str = None) -> str:
        cid = self.add_rect(x, y, w, h, stroke=stroke, bg=bg, frame_id=frame_id)
        current_y = y + 14

        # Badge if present
        if badge:
            bw = min(len(badge) * 9 + 16, w - 30)
            self.add_rect(x + 16, current_y, bw, 22, stroke="transparent", bg=badge_bg, roundness=3, frame_id=frame_id)
            self.add_text(badge, x + 24, current_y + 3, bw, size=11, color=badge_color, frame_id=frame_id)
            current_y += 28

        # Title
        self.add_text(title, x + 16, current_y, w - 32, size=17, color="#172D3E", frame_id=frame_id)
        current_y += 28

        # Body
        if body:
            self.add_text(body, x + 16, current_y, w - 32, size=13, color="#506677", frame_id=frame_id)

        return cid


def build_full_canvas():
    b = ExcalidrawBuilder()

    # Master Banner at Top
    b.add_rect(80, 40, 4700, 110, stroke="#CFD9E0", bg="#0F172A", roundness=3)
    b.add_text("agyFlow · Mapa Visual Integral del Framework Agéntico", 110, 58, 2500, size=32, color="#F8FAFC")
    b.add_text("6 dimensiones operativas para desarrollo de software gobernado por humanos · Compatible con Excalidash y Excalidraw",
               110, 105, 3000, size=16, color="#94A3B8")

    # Dimensions
    FRAME_W = 1500
    FRAME_H = 1200
    GAP_X = 100
    GAP_Y = 100
    ROW1_Y = 190
    ROW2_Y = ROW1_Y + FRAME_H + GAP_Y

    COL1_X = 80
    COL2_X = COL1_X + FRAME_W + GAP_X
    COL3_X = COL2_X + FRAME_W + GAP_X

    # =========================================================================
    # FRAME 1: FILOSOFÍA Y GOBERNANZA HUMANA (HITL)
    # =========================================================================
    f1 = b.add_frame("01 · Filosofía y Gobernanza Humana (HITL)", COL1_X, ROW1_Y, FRAME_W, FRAME_H)
    b.add_rect(COL1_X + 20, ROW1_Y + 20, FRAME_W - 40, 60, stroke="transparent", bg="#EFF6FF", frame_id=f1)
    b.add_text("1. Principio Rector: Human-in-the-Loop & Cero Asunción", COL1_X + 40, ROW1_Y + 35, FRAME_W - 80, size=20, color="#1E40AF", frame_id=f1)

    # Core concept cards
    b.add_card(COL1_X + 40, ROW1_Y + 100, 680, 240,
               "El Humano como Arquitecto y Tech Lead",
               "• La IA NO toma decisiones autónomas de producto ni de arquitectura.\n"
               "• El humano aporta architecture.md, define el stack y aprueba gates.\n"
               "• Ningún agente se autoinvoca ni pasa a la fase siguiente sin aprobación.\n"
               "• Las LLMs operan como desarrolladores junior con alcance delimitado.",
               stroke="#3B82F6", bg="#FFFFFF", badge="Gobernanza Humana", badge_bg="#DBEAFE", badge_color="#1D4ED8", frame_id=f1)

    b.add_card(COL1_X + 760, ROW1_Y + 100, 680, 240,
               "Regla de Cero Asunción",
               "• Prohibido inventar endpoints, tipos o estructuras no verificadas.\n"
               "• Si un contrato no está explícito en packages/contracts: declarar bloqueo.\n"
               "• El conocimiento del proyecto proviene estrictamente de archivos leídos.\n"
               "• Cero bugs reportados NO acredita una prueba exitosa sin evidencia.",
               stroke="#F59E0B", bg="#FFFFFF", badge="Anti-Alucinación", badge_bg="#FEF3C7", badge_color="#B45309", frame_id=f1)

    # Comparison Table / Boxes
    b.add_card(COL1_X + 40, ROW1_Y + 370, 680, 320,
               "❌ Enfoque Agéntico Descontrolado (Frágil)",
               "• Agentes que dialogan entre sí sin gates humanos.\n"
               "• Frontend inventa APIs imaginarias que rompen en runtime.\n"
               "• Bucles infinitos de agentes reintentando código roto.\n"
               "• Despliegues automáticos que publican código no auditado.\n"
               "• Quema masiva de tokens sin entregas de software reales.",
               stroke="#EF4444", bg="#FEF2F2", badge="Antipatrón Común", badge_bg="#FEE2E2", badge_color="#991B1B", frame_id=f1)

    b.add_card(COL1_X + 760, ROW1_Y + 370, 680, 320,
               "✅ Enfoque agyFlow (Ingeniería de Software Real)",
               "• Handshake formal con templates/entrega.md entre roles.\n"
               "• Backend publica contratos Zod primero; Frontend solo los lee.\n"
               "• Circuit breaker: tope de 3 rechazos con escalado a humano.\n"
               "• QA valida revisiones inmutables; DevOps despliega a Staging.\n"
               "• Puerta humana obligatoria para todo despliegue a Producción.",
               stroke="#10B981", bg="#ECFDF5", badge="Estándar de Producción", badge_bg="#D1FAE5", badge_color="#065F46", frame_id=f1)

    # Human Gatekeepers Summary
    b.add_card(COL1_X + 40, ROW1_Y + 720, 1400, 420,
               "Los Tres Gates Humanos Inviolables",
               "1. GATE DE PRD: El humano revisa y aprueba explícitamente el PRD.md antes de que Scrum Master cree tickets en Plane.\n"
               "2. GATE DE CONTRATOS & ARQUITECTURA: El humano define architecture.md. Si diseño y backend difieren, el humano decide.\n"
               "3. GATE DE PRODUCCIÓN: DevOps solo despliega a Staging tras QA aprobado. Producción exige orden humana directa con artefacto exacto.",
               stroke="#6366F1", bg="#F5F3FF", badge="Gates Mandatorios", badge_bg="#EDE9FE", badge_color="#4338CA", frame_id=f1)


    # =========================================================================
    # FRAME 2: EL SQUAD DE 8 AGENTES Y SUS DOMINIOS
    # =========================================================================
    f2 = b.add_frame("02 · El Squad de 8 Agentes y sus Dominios", COL2_X, ROW1_Y, FRAME_W, FRAME_H)
    b.add_rect(COL2_X + 20, ROW1_Y + 20, FRAME_W - 40, 60, stroke="transparent", bg="#F3E8FF", frame_id=f2)
    b.add_text("2. 8 Agentes Especializados con Permisos de Escritura Estrictos", COL2_X + 40, ROW1_Y + 35, FRAME_W - 80, size=20, color="#6B21A8", frame_id=f2)

    agents = [
        ("po-agent", "agy-requirements", "PRD.md e historias de usuario", "NUNCA escribe código ni define estructuras técnicas.", "#3B82F6"),
        ("scrum-master-agent", "agy-planning", "Plane + sprint_actual.md", "Orquesta tareas; 1 escritor por ruta; no toca código de app.", "#6366F1"),
        ("designer-agent", "agy-design-handoff", "Tokens, estilos y assets visuales", "Figma/Pencil; no implementa componentes ni lógica de estado.", "#EC4899"),
        ("backend-dev-agent", "agy-backend-contracts", "packages/contracts + Node/NestJS", "Dueño de contratos Zod; escribe APIs y migraciones con RLS.", "#F59E0B"),
        ("frontend-dev-agent", "agy-frontend-delivery", "apps/web (Next) y apps/site (Astro)", "Solo lectura de contratos; consume tipos vía z.infer; no inventa tipos.", "#10B981"),
        ("qa-agent", "agy-qa-evidence", "tests/ y bug_report.md", "Enfocado en romper; NUNCA arregla el código; dictamen con evidencia.", "#EF4444"),
        ("devops-agent", "agy-build-release", "Docker, CI/CD, docs/deployments/", "Verifica QA aprobado; despliega a Staging; nunca a Prod sin gate.", "#06B6D4"),
        ("automation-agent", "agy-sync-state", "workflows/ (n8n) y sync Plane", "Sincroniza estados y reaperturas; opera solo cuando se le asigna.", "#8B5CF6"),
    ]

    card_w = 680
    card_h = 240
    for idx, (name, skill, domain, rule, color) in enumerate(agents):
        row = idx // 2
        col = idx % 2
        cx = COL2_X + 40 + col * (card_w + 40)
        cy = ROW1_Y + 100 + row * (card_h + 30)

        b.add_card(cx, cy, card_w, card_h,
                   name,
                   f"• Skill: .agents/skills/{skill}/SKILL.md\n"
                   f"• Dominio: {domain}\n"
                   f"• Regla de Oro: {rule}",
                   stroke=color, bg="#FFFFFF", badge="Subagent agyFlow", badge_bg="#F1F5F9", badge_color="#334155", frame_id=f2)


    # =========================================================================
    # FRAME 3: FLUJO DE ENTREGA HANDOFF END-TO-END
    # =========================================================================
    f3 = b.add_frame("03 · Flujo de Entrega Handoff End-to-End", COL3_X, ROW1_Y, FRAME_W, FRAME_H)
    b.add_rect(COL3_X + 20, ROW1_Y + 20, FRAME_W - 40, 60, stroke="transparent", bg="#FEF3C7", frame_id=f3)
    b.add_text("3. Pipeline de Handoff: Del Brief a Staging y Producción", COL3_X + 40, ROW1_Y + 35, FRAME_W - 80, size=20, color="#92400E", frame_id=f3)

    # Vertical sequence of pipeline stages
    stage_w = 400
    stage_h = 130

    # Column A: Brief -> PRD -> Plane
    s1 = b.add_card(COL3_X + 50, ROW1_Y + 110, stage_w, stage_h, "1. Brief Humano", "Aporte de requerimientos iniciales\ny architecture.md antes de fases técnicas.", stroke="#3B82F6", bg="#EFF6FF", badge="Humano", badge_bg="#DBEAFE", badge_color="#1E40AF", frame_id=f3)
    s2 = b.add_card(COL3_X + 50, ROW1_Y + 280, stage_w, stage_h, "2. PO Agent", "Genera PRD.md con criterios Given/When/Then.\nPreguntas abiertas explícitas.", stroke="#3B82F6", bg="#FFFFFF", badge="po-agent", frame_id=f3)
    s3 = b.add_card(COL3_X + 50, ROW1_Y + 450, stage_w, stage_h, "3. Gate Humano PRD", "Persona, fecha y revisión exacta aprobada.\nCondición obligatoria para planificar.", stroke="#10B981", bg="#ECFDF5", badge="Aprobación Humana", badge_bg="#D1FAE5", badge_color="#065F46", frame_id=f3)
    s4 = b.add_card(COL3_X + 50, ROW1_Y + 620, stage_w, stage_h, "4. Scrum Master", "Crea work items en Plane con clave estable.\nGenera espejo sprint_actual.md.", stroke="#6366F1", bg="#FFFFFF", badge="scrum-master", frame_id=f3)

    b.add_arrow(COL3_X + 250, ROW1_Y + 240, COL3_X + 250, ROW1_Y + 280, frame_id=f3)
    b.add_arrow(COL3_X + 250, ROW1_Y + 410, COL3_X + 250, ROW1_Y + 450, frame_id=f3)
    b.add_arrow(COL3_X + 250, ROW1_Y + 580, COL3_X + 250, ROW1_Y + 620, frame_id=f3)

    # Column B: Paralelo (Diseño & Contratos) -> Implementación
    b.add_arrow(COL3_X + 450, ROW1_Y + 685, COL3_X + 530, ROW1_Y + 400, frame_id=f3)
    b.add_arrow(COL3_X + 450, ROW1_Y + 685, COL3_X + 530, ROW1_Y + 620, frame_id=f3)

    s5a = b.add_card(COL3_X + 540, ROW1_Y + 340, stage_w, stage_h, "5a. Designer Agent", "Genera tokens y referencias visuales.\nSeñal de tokens listos para Frontend.", stroke="#EC4899", bg="#FFFFFF", badge="Paralelo: Diseño", frame_id=f3)
    s5b = b.add_card(COL3_X + 540, ROW1_Y + 550, stage_w, stage_h, "5b. Backend Contratos", "Define esquemas Zod en packages/contracts.\nSeñal de contratos listos para Frontend.", stroke="#F59E0B", bg="#FFFFFF", badge="Paralelo: Contratos", frame_id=f3)

    b.add_arrow(COL3_X + 740, ROW1_Y + 470, COL3_X + 740, ROW1_Y + 750, frame_id=f3)
    b.add_arrow(COL3_X + 740, ROW1_Y + 680, COL3_X + 740, ROW1_Y + 750, frame_id=f3)

    s6 = b.add_card(COL3_X + 540, ROW1_Y + 760, stage_w, stage_h, "6. Implementación", "Frontend (apps/web) + Backend (servicios)\nen rutas asignadas con escritor único.", stroke="#10B981", bg="#FFFFFF", badge="Devs", frame_id=f3)

    # Column C: Integración -> QA -> Staging / Escalado
    b.add_arrow(COL3_X + 940, ROW1_Y + 825, COL3_X + 1020, ROW1_Y + 400, frame_id=f3)

    s7 = b.add_card(COL3_X + 1030, ROW1_Y + 340, stage_w, stage_h, "7. QA Agent", "Ejecuta sobre revisión inmutable.\nDictamen: Aprobado / Rechazado / Bloqueado.\nSiempre emite bug_report.md.", stroke="#EF4444", bg="#FFFFFF", badge="Auditoría QA", frame_id=f3)

    # Branch A: Aprobado
    b.add_arrow(COL3_X + 1230, ROW1_Y + 340, COL3_X + 1230, ROW1_Y + 250, color="#10B981", frame_id=f3)
    s8 = b.add_card(COL3_X + 1030, ROW1_Y + 110, stage_w, stage_h, "8. DevOps: Staging", "Verifica QA aprobado exacto.\nBuild + Despliegue a Staging.\nEvidencia en docs/deployments/.", stroke="#06B6D4", bg="#ECFEFF", badge="Aprobado", badge_bg="#CFFAFE", badge_color="#0E7490", frame_id=f3)

    # Branch B: Rechazado & Circuit Breaker
    b.add_arrow(COL3_X + 1230, ROW1_Y + 470, COL3_X + 1230, ROW1_Y + 550, color="#EF4444", frame_id=f3)
    s9 = b.add_card(COL3_X + 1030, ROW1_Y + 550, stage_w, stage_h, "9. Reapertura / Corrección", "Responsable estado registra evento (+1).\nHumano activa fase de corrección.\nRetorna a Devs.", stroke="#EF4444", bg="#FEF2F2", badge="Rechazado", badge_bg="#FEE2E2", badge_color="#991B1B", frame_id=f3)

    b.add_arrow(COL3_X + 1230, ROW1_Y + 680, COL3_X + 1230, ROW1_Y + 760, color="#DC2626", frame_id=f3)
    s10 = b.add_card(COL3_X + 1030, ROW1_Y + 760, stage_w, stage_h, "10. Circuit Breaker", "≥3 rechazos consecutivos en Plane.\nCongela reasignación automática.\nEscala a intervención humana.", stroke="#B91C1C", bg="#FEF2F2", badge="Escalado Humano", badge_bg="#F87171", badge_color="#7F1D1D", frame_id=f3)

    b.add_card(COL3_X + 50, ROW1_Y + 950, 1400, 190,
               "Resumen de Transición entre Fases (Handoff)",
               "• Formato obligatorio de traspaso en cada respuesta: templates/entrega.md\n"
               "• Comando de generación asistida de prompt: python3 scripts/handoff.py prompt --to <rol> --ticket <ID>\n"
               "• Verificación de precondiciones: python3 scripts/handoff.py check --role <rol> --input <archivo>",
               stroke="#64748B", bg="#F8FAFC", badge="Estandarización", frame_id=f3)


    # =========================================================================
    # FRAME 4: LAS TRES REGLAS DE ORO OPERATIVAS
    # =========================================================================
    f4 = b.add_frame("04 · Las Tres Reglas de Oro Operativas", COL1_X, ROW2_Y, FRAME_W, FRAME_H)
    b.add_rect(COL1_X + 20, ROW2_Y + 20, FRAME_W - 40, 60, stroke="transparent", bg="#FEF2F2", frame_id=f4)
    b.add_text("4. Las Tres Salvaguardas No Negociables del Squad", COL1_X + 40, ROW2_Y + 35, FRAME_W - 80, size=20, color="#991B1B", frame_id=f4)

    # 3 big pillars
    col_w = 440
    b.add_card(COL1_X + 40, ROW2_Y + 110, col_w, 980,
               "REGLA 1: CERO ASUNCIÓN",
               "Principio Fundamental:\n"
               "El conocimiento del proyecto proviene exclusivamente de los archivos leídos en la sesión actual.\n\n"
               "Normas Operativas:\n"
               "• Si un tipo de API, esquema de base de datos o parámetro no existe en packages/contracts: prohibido inventarlo.\n\n"
               "• El agente debe detenerse y reportar el bloqueo formalmente en su respuesta de entrega.\n\n"
               "• Frontend Dev NUNCA define tipos de dominio locales para saltarse contratos pendientes.\n\n"
               "• QA NUNCA asume que la ausencia de fallos equivale a criterios cumplidos.\n\n"
               "• DevOps NUNCA asume que un build exitoso sustituye a un dictamen de QA aprobado.\n\n"
               "Beneficio:\n"
               "Elimina el 99% de las alucinaciones estructurales típicas de las IAs.",
               stroke="#DC2626", bg="#FFFFFF", badge="Anti-Hallucination", badge_bg="#FEE2E2", badge_color="#991B1B", frame_id=f4)

    b.add_card(COL1_X + 520, ROW2_Y + 110, col_w, 980,
               "REGLA 2: CIRCUIT BREAKER",
               "Control de Bucles Infinitos:\n"
               "Previene que los agentes quemen tokens reintentando eternamente el mismo fallo.\n\n"
               "Mecanismo en Plane:\n"
               "• Cada ejecución de QA tiene clave estable única:\n"
               "  ticket:revision:ejecucion-qa\n\n"
               "• Un reintento por timeout no incrementa el contador de reaperturas.\n\n"
               "• Solo un rechazo vigente por ejecución distinta suma +1 al contador.\n\n"
               "• Al llegar a 3 reaperturas consecutivas:\n"
               "  1. Estado pasa a 'escalado'.\n"
               "  2. Se cancela la reasignación automática.\n"
               "  3. Se exige intervención humana directa para destrabar el ticket.\n\n"
               "• Dictamen tardío no altera el estado del ticket.",
               stroke="#F59E0B", bg="#FFFFFF", badge="Anti-Loop", badge_bg="#FEF3C7", badge_color="#B45309", frame_id=f4)

    b.add_card(COL1_X + 1000, ROW2_Y + 110, col_w, 980,
               "REGLA 3: UN SOLO ESCRITOR",
               "Aislamiento Concurrente:\n"
               "Permite que sesiones paralelas (agy y Codex) trabajen juntas sin pisarse.\n\n"
               "Políticas de Reparto:\n"
               "• En una misma carpeta o módulo, cada archivo tiene exactamente UN único escritor asignado.\n\n"
               "• Scrum Master registra las rutas exclusivas en el sprint antes de habilitar tareas concurrentes.\n\n"
               "• Archivos compartidos (manifests, package.json, lockfiles) tienen un dueño técnico único coordinado.\n\n"
               "• Si se detecta colisión de edición:\n"
               "  Se detiene la escritura de inmediato y se solicita reasignación al Scrum Master.\n\n"
               "• Separación física mediante git worktrees en ramas separadas si es necesario.",
               stroke="#3B82F6", bg="#FFFFFF", badge="Aislamiento", badge_bg="#DBEAFE", badge_color="#1D4ED8", frame_id=f4)


    # =========================================================================
    # FRAME 5: EL KIT DE HERRAMIENTAS Y AUTOMATIZACIÓN CLI
    # =========================================================================
    f5 = b.add_frame("05 · Kit de Herramientas y Automatización CLI", COL2_X, ROW2_Y, FRAME_W, FRAME_H)
    b.add_rect(COL2_X + 20, ROW2_Y + 20, FRAME_W - 40, 60, stroke="transparent", bg="#F0FDF4", frame_id=f5)
    b.add_text("5. Infraestructura de Validación, Handoff y Scaffolding", COL2_X + 40, ROW2_Y + 35, FRAME_W - 80, size=20, color="#166534", frame_id=f5)

    tool_w = 680
    tool_h = 240

    b.add_card(COL2_X + 40, ROW2_Y + 100, tool_w, tool_h,
               "scripts/validate_squad.py",
               "• Validador hermético sin llamadas de red ni secretos.\n"
               "• Comprueba frontmatter, subagent: true, y consistencia de nombres.\n"
               "• Verifica existencia de las 8 skills bundled en .agents/skills/.\n"
               "• Exige referencias obligatorias a stack.md, entrega.md y protocolo.md.\n"
               "• Modo --project valida que el receptor tenga arquitectura y contratos.",
               stroke="#10B981", bg="#FFFFFF", badge="Auditoría Squad", badge_bg="#D1FAE5", badge_color="#065F46", frame_id=f5)

    b.add_card(COL2_X + 760, ROW2_Y + 100, tool_w, tool_h,
               "scripts/handoff.py",
               "• Subcomando prompt: genera el prompt exacto para invocar agy --agent.\n"
               "• Subcomando check: audita si las precondiciones de fase están cumplidas.\n"
               "• Subcomando template: emite plantillas pre-completadas de entrega.md.\n"
               "• Inyecta sesión agy-1, rutas asignadas y contexto de la entrega anterior.\n"
               "• Probado con 6 tests unitarios en tests/test_handoff.py.",
               stroke="#6366F1", bg="#FFFFFF", badge="Handoff Runner", badge_bg="#EDE9FE", badge_color="#4338CA", frame_id=f5)

    b.add_card(COL2_X + 40, ROW2_Y + 370, tool_w, tool_h,
               "scripts/setup_receiver.py",
               "• Scaffolding guiado interactivo o desatendido para proyectos nuevos.\n"
               "• Flags: --frontend (next/astro), --backend (nest/node), --db (supabase/postgres).\n"
               "• Genera architecture.md con las decisiones humanas seleccionadas.\n"
               "• Inicializa PRD.md, sprint_actual.md y packages/contracts/src/index.ts.\n"
               "• Protege contra sobreescritura sin flag --force.",
               stroke="#F59E0B", bg="#FFFFFF", badge="Scaffolding CLI", badge_bg="#FEF3C7", badge_color="#B45309", frame_id=f5)

    b.add_card(COL2_X + 760, ROW2_Y + 370, tool_w, tool_h,
               "CI/CD & Suite de 24 Pruebas Unitarias",
               "• GitHub Actions (.github/workflows/validate-squad.yml) en Py 3.10/3.11/3.12.\n"
               "• Configuración pre-commit (.pre-commit-config.yaml) para higiene local.\n"
               "• 24 tests unitarios ejecutados en 0.6s con unittest estándar.\n"
               "• 15 tests de paquete + 6 tests de handoff + 3 tests de setup_receiver.\n"
               "• 100% de cobertura en reglas de validación y portabilidad.",
               stroke="#06B6D4", bg="#FFFFFF", badge="Calidad Continua", badge_bg="#CFFAFE", badge_color="#0E7490", frame_id=f5)

    # Espejo Sprint Rediseñado
    b.add_card(COL2_X + 40, ROW2_Y + 640, 1400, 500,
               "Rediseño del Espejo: templates/sprint_actual.md",
               "Arquitectura en Dos Capas (Eliminó la tabla frágil de 12 columnas):\n\n"
               "1. CAPA DE RESUMEN (Compacta, 5 columnas, sin scroll horizontal):\n"
               "   | Ticket / ID | Clave estable | Responsable | Estado | Reaperturas |\n"
               "   | PROJ-101 | auth:login:form | frontend-dev-agent | listo | 0 |\n\n"
               "2. CAPA DE DETALLE ESTRUCTURADO (Bloques Markdown por tarea con 12 atributos):\n"
               "   ### [PROJ-101] Formulario de Inicio de Sesión\n"
               "   - Clave estable: auth:login:form\n"
               "   - Responsable: frontend-dev-agent\n"
               "   - Dependencias: packages/contracts/src/auth.schema.ts@rev-12a (listo)\n"
               "   - Rutas asignadas: apps/web/src/features/auth/\n"
               "   - Evidencia QA: bug_report.md (aprobado rev-abc)\n"
               "   - Reaperturas: 0 (máximo 3 antes de escalado humano)",
               stroke="#64748B", bg="#F8FAFC", badge="Formato Robusto", frame_id=f5)


    # =========================================================================
    # FRAME 6: CÓMO SE USA EN LA PRÁCTICA (PROYECTO RECEPTOR)
    # =========================================================================
    f6 = b.add_frame("06 · Cómo se Usa en la Práctica (Proyecto Receptor)", COL3_X, ROW2_Y, FRAME_W, FRAME_H)
    b.add_rect(COL3_X + 20, ROW2_Y + 20, FRAME_W - 40, 60, stroke="transparent", bg="#EFF6FF", frame_id=f6)
    b.add_text("6. Guía Paso a Paso para Desarrollar un Producto Real", COL3_X + 40, ROW2_Y + 35, FRAME_W - 80, size=20, color="#1E40AF", frame_id=f6)

    steps = [
        ("Paso 1: Inicializar Proyecto", "python3 scripts/setup_receiver.py --target ~/mi-app --frontend next --backend nestjs --db supabase\nGenera arquitectura y contratos base.", "#3B82F6"),
        ("Paso 2: Brief & PRD", "El humano entrega brief a agy --agent po-agent.\nEl PO genera PRD.md con criterios verificables. El humano revisa y firma.", "#6366F1"),
        ("Paso 3: Planificación en Plane", "Scrum Master lee PRD aprobado y crea épicas y work items en Plane.\nGenera sprint_actual.md con escritor único por ruta.", "#8B5CF6"),
        ("Paso 4: Contratos y Diseño", "Backend escribe schemas Zod en packages/contracts/.\nDesigner entrega tokens en Figma/Pencil. Ambos emiten señal de listo.", "#EC4899"),
        ("Paso 5: Handoff a Implementación", "Usar python3 scripts/handoff.py prompt --from backend --to frontend ...\nFrontend implementa sabiendo que los contratos son definitivos.", "#10B981"),
        ("Paso 6: QA, Staging y Producción", "QA ejecuta Playwright sobre revisión inmutable y emite bug_report.md.\nSi aprueba: DevOps despliega a Staging. Humano autoriza Producción.", "#F59E0B"),
    ]

    for idx, (title, desc, col) in enumerate(steps):
        sy = ROW2_Y + 110 + idx * 170
        b.add_card(COL3_X + 40, sy, 1400, 145,
                   title, desc,
                   stroke=col, bg="#FFFFFF", badge=f"Etapa 0{idx+1}", badge_bg="#F1F5F9", badge_color="#334155", frame_id=f6)

    return {
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": b.elements,
        "appState": {
            "gridSize": None,
            "viewBackgroundColor": "#F8FAFC",
            "theme": "light",
            "exportBackground": True,
            "exportWithDarkMode": False,
            "exportScale": 2
        },
        "files": {}
    }


def generate_svg_preview(canvas_data: dict, out_svg_path: Path):
    """Generate a clean SVG preview of the Excalidraw canvas."""
    elements = canvas_data["elements"]
    min_x = min(e.get("x", 0) for e in elements) - 40
    min_y = min(e.get("y", 0) for e in elements) - 40
    max_x = max(e.get("x", 0) + e.get("width", 0) for e in elements) + 40
    max_y = max(e.get("y", 0) + e.get("height", 0) for e in elements) + 40
    width = max_x - min_x
    height = max_y - min_y

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{min_x} {min_y} {width} {height}" width="{width}" height="{height}">',
        f'<rect x="{min_x}" y="{min_y}" width="{width}" height="{height}" fill="#F8FAFC" />',
        '<style>',
        '  text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }',
        '</style>'
    ]

    for e in elements:
        t = e.get("type")
        x = e.get("x", 0)
        y = e.get("y", 0)
        w = e.get("width", 0)
        h = e.get("height", 0)
        stroke = e.get("strokeColor", "#000")
        bg = e.get("backgroundColor", "transparent")
        sw = e.get("strokeWidth", 1)

        if t == "frame":
            svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{stroke}" stroke-width="{sw}" stroke-dasharray="6,6" rx="8" />')
            name = e.get("name", "")
            if name:
                svg.append(f'<text x="{x + 20}" y="{y - 12}" font-size="20" font-weight="bold" fill="#334155">{name}</text>')

        elif t == "rectangle":
            rx = 8 if e.get("roundness") else 0
            svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{bg}" stroke="{stroke}" stroke-width="{sw}" rx="{rx}" />')

        elif t == "text":
            fs = e.get("fontSize", 14)
            lines = e.get("text", "").split("\n")
            weight = "bold" if fs >= 18 else "normal"
            for idx, line in enumerate(lines):
                ly = y + (idx + 1) * (fs * 1.3)
                escaped = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                svg.append(f'<text x="{x}" y="{ly}" font-size="{fs}" font-weight="{weight}" fill="{stroke}">{escaped}</text>')

        elif t == "arrow":
            points = e.get("points", [[0, 0], [0, 0]])
            if len(points) >= 2:
                x1, y1 = x + points[0][0], y + points[0][1]
                x2, y2 = x + points[1][0], y + points[1][1]
                svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}" marker-end="url(#arrowhead)" />')

    # Marker def for arrows
    svg.insert(3, '''<defs>
      <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
        <polygon points="0 0, 10 3.5, 0 7" fill="#8195A3" />
      </marker>
    </defs>''')

    svg.append('</svg>')
    out_svg_path.write_text("\n".join(svg), encoding="utf-8")


def main():
    canvas = build_full_canvas()
    excalidraw_path = OUT_DIR / "agyflow-flujo-completo.excalidraw"
    with open(excalidraw_path, "w", encoding="utf-8") as f:
        json.dump(canvas, f, indent=2, ensure_ascii=False)
    print(f"Canvas Excalidraw generado: {excalidraw_path} ({len(canvas['elements'])} elementos)")

    svg_path = OUT_DIR / "agyflow-flujo-completo.svg"
    generate_svg_preview(canvas, svg_path)
    print(f"Vista previa SVG generada: {svg_path}")


if __name__ == "__main__":
    main()

---
name: agy-security-audit
description: Auditar seguridad, políticas de acceso RLS, contratos y OWASP Top 10 para QA y Backend en agyFlow sin exponer secretos.
---

# Auditoría de seguridad y hardening

Las rutas mencionadas son relativas a la raíz del proyecto receptor.
Aplicá `docs/protocolo.md` para límites de escritura y reporte de hallazgos.
Esta skill proporciona el procedimiento de auditoría defensiva para el backend y QA;
no autoriza ataques destructivos, inyecciones en producción ni divulgación de credenciales.

## Procedimiento de auditoría

1. **Autenticación y tokens**:
   - Comprobá que las rutas privadas exijan validación criptográfica del token (JWT).
   - Verificá que el frontend no almacene tokens de sesión en `localStorage` si maneja datos sensibles (preferir cookies `HttpOnly; Secure; SameSite=Lax/Strict`).
   - Auditá que la expiración del token y la revocación estén implementadas.

2. **Seguridad en base de datos (RLS obligatorio)**:
   - En proyectos con Supabase o PostgreSQL, NINGUNA tabla pública debe carecer de Row Level Security (`ALTER TABLE <tabla> ENABLE ROW LEVEL SECURITY;`).
   - Auditá que las políticas RLS no usen condiciones triviales como `USING (true)` para escrituras o lecturas de datos de otros usuarios.
   - Verificá que los accesos por ID de usuario comparen contra el `auth.uid()` del contexto de sesión y no contra un parámetro enviado por el cliente (prevención de IDOR).

3. **Validación de esquemas y sanitización (Zod)**:
   - Toda entrada de API debe validarse estrictamente contra un esquema Zod en `packages/contracts`.
   - Rechazá campos desconocidos no declarados (`.strict()` en Zod cuando aplique).
   - Verificá que no se concatenen parámetros directamente en consultas SQL o llamadas al sistema (prevención de SQLi y Command Injection).

4. **Fuga de secretos y credenciales**:
   - Inspeccioná que ningún archivo versionado contenga cadenas que parezcan API keys, service role keys, contraseñas o tokens privados.
   - Comprobá que `.env` esté listado en `.gitignore` y que solo `.env.example` esté presente con valores ficticios.
   - Las claves de servicio privilegiadas (ej. `SUPABASE_SERVICE_ROLE_KEY`) NUNCA deben exponerse al cliente (frontend).

5. **Cabeceras HTTP y CORS**:
   - Verificá que CORS restrinja orígenes permitidos y no use `*` con credenciales activas.
   - Comprobá la presencia de cabeceras de seguridad: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Content-Security-Policy`.

## Emisión de hallazgos

Si QA o Backend detectan una vulnerabilidad:
- Registrá el hallazgo en `bug_report.md` con severidad `bloqueante` (Crítica / Alta) o `media`.
- Incluí: vector de ataque conceptual, impacto potencial, precondición y remediación recomendada en el contrato o servicio.
- Un fallo de seguridad crítico en la revisión candidata IMPIDE la emisión de un dictamen aprobado.

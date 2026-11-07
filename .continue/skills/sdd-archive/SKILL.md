"# Skill: sdd-archive

> Al cerrar, marca el spec como implementado y lo mueve a su histórico.

## Cuándo se activa
Después de `close-feature` (y opcionalmente `sdd-verify`), solo en rama SDD.

## Pasos

1. **Marcar** en `specs/<feature>/spec.md`:
   ```markdown
   > **Estado**: ✅ Implementado (<fecha>)
   > **Feature doc**: [odd/tasks/<feature>.md](../../odd/tasks/<feature>.md)
   ```
2. **Mover** a histórico:
   ```
   specs/<feature>/  →  specs/_archive/<feature>/
   ```
3. **Actualizar** `odd/tasks/<feature>.md` sección `## Close`:
   - "Spec archivado en `specs/_archive/<feature>/`"
4. **Commit**: `chore: archive spec <feature>`

## Reglas
- Solo se archiva si `close-feature` está completo.
- El spec archivado es inmutable (no se edita más).
- Si se necesita reabrir → se crea nueva feature (no se reabre el archivado).
- El archivo `odd/tasks/<feature>.md` NO se mueve (es el histórico de progreso).
"
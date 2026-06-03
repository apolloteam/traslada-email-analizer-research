# Convenciones de Git Commits

- Usar el estándar Conventional Commits para todos los mensajes de commit.
  - Formato: `<tipo>[scope opcional]: <descripción>`.
  - Tipos permitidos: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`, `ci`, `build`.
  - La descripción en minúsculas y en español.
  - Si el cambio rompe compatibilidad, agregar `!` antes de `:` o footer `BREAKING CHANGE:`.
  - Usar verbo en tercera persona del singular (presente indicativo) en la descripción, no infinitivo.
    La descripción debe completar la frase "Si se aplica, este commit..."
    ✓ "feat: agrega validación de email"
    ✗ "feat: agregar validación de email"
- Siempre mostrar el mensaje del commit propuesto y esperar confirmación antes de ejecutarlo.
- NUNCA agregar trailers al commit (ni "Co-Authored-By", ni "Generated-by", ni ningún footer automático).

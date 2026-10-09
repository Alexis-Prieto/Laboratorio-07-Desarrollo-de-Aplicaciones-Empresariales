# Lab 07 — ORM con IA: duelo y verificador

Proyecto Django 5.2 (Python 3.13, SQLite) para el Laboratorio N°7 del curso
*Desarrollo de Aplicaciones Empresariales*. Audita consultas ORM, ejecuta un
duelo equipo-vs-IA, optimiza N+1 y prueba un agente controlado.

Trabajo individual — Alexis Prieto Huiza.

## Puesta en marcha

```bash
python -m pip install "Django>=5.0,<5.3"
python manage.py migrate
python manage.py seed_blog
```

## Comandos del laboratorio

```bash
# Duelo ORM: equipo (8/8) vs IA (source guiado) vs IA desde cero
python manage.py duel                    # source=team
python manage.py duel --source ai
python manage.py duel --source ai_fresh

# Prueba de consultas N+1 del front page (de 23 a 2 consultas)
python manage.py test blog.tests.test_front_page -v 2
python manage.py test

# Agente controlado (4 intenciones del README)
python manage.py agent --intent 'list_posts'                    # ok
python manage.py agent --intent 'delete_comments_of_post'       # approval_required
python manage.py agent --intent 'drop_table'                    # denied
python manage.py agent --intent 'raw_sql'                       # denied

# Prompt injection: leer comentarios del post 1 (el 4º es malicioso)
python manage.py agent --intent 'comments_of_post' --post-id 1

# Aprobación con hash (destructiva). 1) plan, 2) approve <HASH>
python manage.py agent --intent 'delete_comments_of_post' --post-id 5
python manage.py agent --intent 'delete_comments_of_post' --post-id 5 --approve <HASH>

# Restaurar datos tras la práctica de borrado
python manage.py seed_blog
```

## Estructura

- `blog/models.py` — Author, Profile, Category, Tag, Post, Comment.
- `blog/queries.py` — front page optimizado (select_related + prefetch_related).
- `blog/duel/` — preguntas (`questions.py`), respuestas del equipo (`team.py`)
  y de la IA (`ai.py`, `ai_fresh.py`).
- `blog/agent/` — `registry.py` (whitelist/denylist/validación) y
  `executor.py` (plan + hash de aprobación).
- `evidence/` — salidas crudas de cada comando ejecutado.
- `ENTREGABLE_LAB07.md` — informe completo del laboratorio.

## Notas de seguridad (resumen)

- Sin credenciales en el código: `config/settings.py` lee del entorno.
- El agente solo ejecuta intenciones en la whitelist; `raw_sql`/`drop_table`
  están denegados. Las acciones destructivas exigen un hash de aprobación que se
  invalida si los datos cambian entre el plan y la aprobación.

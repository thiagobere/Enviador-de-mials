"""Email templates for sponsorship outreach."""

from sponsor_bot.config import (
    PILOT_NAME, PILOT_IG_FOLLOWERS, PILOT_MONTHLY_VIEWS,
    PILOT_COUNTRY, EMAIL_SUBJECT_TEMPLATE
)


def get_subject(company: str) -> str:
    return EMAIL_SUBJECT_TEMPLATE.format(company=company)


def get_outreach_email_html(company: str, contact_name: str = "", language: str = "en") -> str:
    """Returns the HTML body for a sponsorship outreach email."""
    if language == "es":
        return _outreach_es(company, contact_name)
    return _outreach_en(company, contact_name)


def _outreach_en(company: str, contact_name: str) -> str:
    greeting = f"Dear {contact_name}," if contact_name else f"Dear {company} Partnerships Team,"
    return f"""
<html><body style="font-family: Arial, sans-serif; font-size: 15px; color: #222; max-width: 680px;">

<p>{greeting}</p>

<p>My name is <strong>{PILOT_NAME}</strong>, a karting pilot and content creator from {PILOT_COUNTRY}.
I compete in karting championships while building an engaged community around motorsport and real racing.</p>

<p><strong>My reach:</strong></p>
<ul>
  <li>📸 <strong>{PILOT_IG_FOLLOWERS} Instagram followers</strong> with up to <strong>{PILOT_MONTHLY_VIEWS} monthly views</strong></li>
  <li>🎥 YouTube channel covering karting races, technical content, and behind-the-scenes</li>
  <li>🏁 Active karting competitor – real racing, real audience</li>
  <li>🎓 Engineering student – technical credibility for motorsport & tech brands</li>
</ul>

<p><strong>What I offer as your brand ambassador:</strong></p>
<ul>
  <li>Branded content on Instagram and YouTube (posts, reels, race coverage)</li>
  <li>Logo placement on kart, helmet, and racing suit</li>
  <li>Authentic promotion to a passionate motorsport audience in Latin America and worldwide</li>
  <li>Flexible partnership tiers (product sponsorship or financial support)</li>
</ul>

<p>I believe {company}'s values align perfectly with competitive motorsport and authentic content creation.
I would love to explore a partnership that benefits both sides — whether it's product support,
co-branded content, or a more comprehensive ambassadorship.</p>

<p>Would you be open to a brief call or email exchange to discuss possibilities?</p>

<p>Best regards,<br>
<strong>{PILOT_NAME}</strong><br>
Karting Pilot & Content Creator<br>
Instagram: @thiago_berenstein<br>
{PILOT_COUNTRY}</p>

</body></html>
"""


def _outreach_es(company: str, contact_name: str) -> str:
    greeting = f"Hola {contact_name}," if contact_name else f"Estimado equipo de {company},"
    return f"""
<html><body style="font-family: Arial, sans-serif; font-size: 15px; color: #222; max-width: 680px;">

<p>{greeting}</p>

<p>Mi nombre es <strong>{PILOT_NAME}</strong>, piloto de karting y creador de contenido de {PILOT_COUNTRY}.
Compito en campeonatos de karting mientras construyo una comunidad activa en torno al automovilismo y las carreras reales.</p>

<p><strong>Mi alcance:</strong></p>
<ul>
  <li>📸 <strong>{PILOT_IG_FOLLOWERS} seguidores en Instagram</strong> con hasta <strong>{PILOT_MONTHLY_VIEWS} vistas mensuales</strong></li>
  <li>🎥 Canal de YouTube con cobertura de karting, contenido técnico y detrás de escena</li>
  <li>🏁 Piloto activo de karting – carreras reales, audiencia real</li>
  <li>🎓 Estudiante de ingeniería – credibilidad técnica para marcas de tecnología y motorsport</li>
</ul>

<p><strong>Lo que ofrezco como embajador de tu marca:</strong></p>
<ul>
  <li>Contenido con branding en Instagram y YouTube (posts, reels, cobertura de carreras)</li>
  <li>Logo en kart, casco y traje de carrera</li>
  <li>Promoción auténtica a una audiencia apasionada por el motorsport en Latinoamérica y el mundo</li>
  <li>Tiers de partnership flexibles (sponsor de producto o apoyo económico)</li>
</ul>

<p>Creo que los valores de {company} se alinean perfectamente con el motorsport competitivo y la creación de contenido auténtico.
Me encantaría explorar una colaboración que beneficie a ambas partes.</p>

<p>¿Estarías disponible para una breve llamada o intercambio de emails para discutir posibilidades?</p>

<p>Saludos,<br>
<strong>{PILOT_NAME}</strong><br>
Piloto de Karting y Creador de Contenido<br>
Instagram: @thiago_berenstein<br>
{PILOT_COUNTRY}</p>

</body></html>
"""


def get_followup_email_html(company: str, original_date: str, language: str = "en") -> str:
    if language == "es":
        return f"""<html><body style="font-family: Arial, sans-serif; font-size: 15px; color: #222; max-width: 680px;">
<p>Estimado equipo de {company},</p>
<p>Quería hacer un seguimiento de mi email del {original_date} sobre una posible partnership de sponsorship.</p>
<p>Si tuvieras un momento para revisar mi propuesta, me encantaría conversar sobre cómo podría representar a {company} en mis actividades de karting y contenido.</p>
<p>Quedo a disposición para cualquier pregunta.</p>
<p>Saludos,<br><strong>{PILOT_NAME}</strong><br>Piloto de Karting | @thiago_berenstein</p>
</body></html>"""
    return f"""<html><body style="font-family: Arial, sans-serif; font-size: 15px; color: #222; max-width: 680px;">
<p>Dear {company} Team,</p>
<p>I wanted to follow up on my email from {original_date} regarding a potential sponsorship partnership.</p>
<p>If you have a moment to review my proposal, I'd love to discuss how I could represent {company} in my karting activities and content creation.</p>
<p>Happy to answer any questions you might have.</p>
<p>Best regards,<br><strong>{PILOT_NAME}</strong><br>Karting Pilot | @thiago_berenstein</p>
</body></html>"""

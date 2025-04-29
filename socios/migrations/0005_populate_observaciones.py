from django.db import migrations
from datetime import date
from django.utils.timezone import now

def cargar_observaciones_estaticas(apps, schema_editor):
    Socio = apps.get_model('socios', 'Socio')
    Observacion = apps.get_model('socios', 'Observacion')

    hoy = now().date()

    # 🔥 Datos estáticos de socios y observaciones
    observaciones = [
        ("Aggio Diego","rodilla"),
        ("Albornoz Mari","Rodilla-Progresivo"),
        ("Aliano Ana Laura","progresivo hombro"),
        ("Alvarez Sol","Cervicales"),
        ("Amigutty jose","Dolor cervical"),
        ("Amoros Santi","Hombro"),
        ("Arroyo Celeste","progresivo"),
        ("Balumbo Lupe","progresivo"),
        ("barbi","rodilla/movilidad cadera"),
        ("Basso Ines","sin impacto"),
        ("Benavides Negro","rodilla "),
        ("Benavides Rafa","rodilla/cadera"),
        ("Bos Yanina","Lumbar/espolon"),
        ("Brondo Male","Cervicalgia"),
        ("Bruno Mauro","isquios cortos"),
        ("Bustos Gimena","progresivo"),
        ("Caloni Nico","Tobillo (Fort. gemelos)"),
        ("Campana Marcela","hombros"),
        ("Cano Marcela","sin impacto"),
        ("Cañete Jose","hombros"),
        ("Carusso Mia","trabajar dorsales"),
        ("Castro Nico","Cervicalgia"),
        ("Cejas Vanesa ","S/A hace 4 meses "),
        ("Centioli Mari","Cervicalgia"),
        ("Cristian Loriega","Corregir postura"),
        ("Curti Valentina","Cadera/rodilla - Progresivo"),
        ("Dandrilli dani","Dolor lumbar alta"),
        ("Diaz Rosario","esguince tobillo (viejo)"),
        ("Diz Juli","cervicales (no hace bb)"),
        ("Dominguez Vale","muñecas"),
        ("Dufayard ale","hombros"),
        ("Dumanski Cristina","Lumbar"),
        ("Echegaray Moni","cervicalgia"),
        ("Edu","rodilla "),
        ("Espil Juli","trabajar espalda-cuadriceps"),
        ("Fardauz Lucas","Controlar pesos y tecnica"),
        ("Fernandez Graciela","Rodillas-Progresivo fortalecimiento"),
        ("Ferraz Oriana","Progresivo"),
        ("Figiolo Sol","rodilla"),
        ("Forni Anto","no estocadas"),
        ("Furiati Ana","sin impacto"),
        ("Gaitan Mariana","Progresivo"),
        ("gallegos leo","hernia lumbar"),
        ("Garau Lili","Cuidar cervical"),
        ("Gasparini Pilar","rodilla"),
        ("Giachino Mari luz","progresivo abs pirnas"),
        ("Gomez Nati","rodilla"),
        ("Gonzalez Estefania","Fortalecer hombro/progresivo"),
        ("Gorosito Vir","tobillo"),
        ("Guarino Valen","Equitacion"),
        ("Haydee Scorzato","progresivo (quiere musc.)"),
        ("Hever Ceci","rodillas"),
        ("Ibarbuden Cami","progresivo"),
        ("laclotte carla","cintura"),
        ("Ledesma Matias","hace musculacion (rodilla a veces) viene x fun."),
        ("Lombardo Nati","Cervicalgia/osteoporosis"),
        ("Lopez Sergio","hombro"),
        ("Luciaw Mari","rodilla"),
        ("Mancuso Tere","dolor de hombro(v.fron.lat.)"),
        ("Marazzo Agos","Tenditis tobillo sin imp."),
        ("Martin Flor","rodilla"),
        ("Martini Omar","lesion tobillo desgarro cuadriceps"),
        ("Masino Sofi","rodilla"),
        ("Menendez Adriana","sin colcho"),
        ("Negri Gaspar","Fisura Lumbar"),
        ("Nicastro Monica","artrosis cervical"),
        ("Nicosia Albert","rodilla"),
        ("Noriega Cristian","corregir tecnica"),
        ("Oberti Marcelo","abomb. lumb. Cadera rodilla / progresivo"),
        ("Orellano Caro","cervicales"),
        ("Papaleo Cele","cervicalgia"),
        ("Parra Andres","corregir posturas"),
        ("Parra Diego","tendinitis rotuliano"),
        ("Pascarelli Marce","movilidad y estab."),
        ("Paz Lujan","Progresivo"),
        ("Perez Mariana","progresivo"),
        ("Platon Ana","Dolor lumbar-No abdominaes-No sentadillas"),
        ("Ponti Belen","progresivo"),
        ("Poza Luli","Problema rodilla"),
        ("Poza Rodrigo","rodilla"),
        ("Priano Pau","art. cadera/ hernia Lumb."),
        ("Puyos Carla","Condromalasia rotuliana"),
        ("Quevedo yani","cervicales-muñecas"),
        ("Reynoso Vanesa","cervicales"),
        ("Rocha Ricardo","Hernia inguinal/progresivo"),
        ("Rosso Marcela","hernia lumbar/hombro"),
        ("Salinas Fausto","lumbares. trabajar postura"),
        ("Salinas Pablo","lumbares, rodilla, dolor inguinal"),
        ("Sanchez maria del carmen","Progresivo"),
        ("Santiago Sil","Dolor Cervical"),
        ("Sartor Soledad","progresivo "),
        ("Scardulla Wendy","rodilla-muñeca"),
        ("Segura Carlos","Solo movilidad"),
        ("Sela Pablo","malla abdominal"),
        ("Silva Ana","progresivo"),
        ("Solari Sofi","Rodilla"),
        ("Somma Juli","tobillo"),
        ("Soto Claudio","Hernias lumbares/rodilla"),
        ("Suarez Santino","Futbol (Trabajar pot.)"),
        ("Tiberi Alberto","Dolor de rodilla"),
        ("Tomas Pia","progresivo"),
        ("Torres Aldo (tobi)","Ciatico"),
        ("Torres Erica","cirugia abdomial"),
        ("Vigione Ana","S/impacto"),
        ("Vilches Daniel","progresivo "),
        ("Vilches Estefnia","cintura"),
        ("Vitale beto","rotuliano y aquiles"),
        ("Vitale Milagros","placas en muñeca"),
        ("Zafalon Mica","Ciatico-muñca"),
        ("Zeppa Delfi","8 años"),
        ("Zeppa Ernes","progresivo"),
        ("Zeppa Vicky","Dolor de hombro")
    ]

    for socio_apellido_nombre, descripcion in observaciones:
        partes = socio_apellido_nombre.split(' ', 1)
        if len(partes) == 2:
            apellido, nombre = partes
        else:
            apellido, nombre = partes[0], ''

        apellido = apellido.strip().capitalize()
        nombre = nombre.strip().capitalize()

        try:
            socio = Socio.objects.get(nombre__iexact=nombre, apellido__iexact=apellido)
            Observacion.objects.create(
                socio=socio,
                descripcion=descripcion,
                fecha_inicio=hoy,
                fecha_fin=None
            )
            print(f"✔️ Observación creada para {apellido} {nombre}: {descripcion}")
        except Socio.DoesNotExist:
            print(f"⚠️ No se encontró el socio: '{apellido} {nombre}'")
        except Exception as e:
            print(f"❌ Error creando observación para '{apellido} {nombre}': {e}")

def revertir_observaciones_estaticas(apps, schema_editor):
    Observacion = apps.get_model('socios', 'Observacion')
    Observacion.objects.filter(fecha_inicio=date.today()).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('socios', '0004_observacion_delete_pago'),  # Actualizalo bien acá
    ]

    operations = [
        migrations.RunPython(cargar_observaciones_estaticas, revertir_observaciones_estaticas),
    ]


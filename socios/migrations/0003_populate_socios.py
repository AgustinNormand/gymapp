from django.db import migrations
import os

def cargar_socios(apps, schema_editor):
    Socio = apps.get_model('socios', 'Socio')

    raw_users = "Aggio Diego,Albornoz Mari,Alfano Ariel,Aliano Ana Laura,Almada Aye,Alvarez Sol,Amiguetti Pity,Amigutty jose,Amoros Santi,Arroyo Celeste,Balumbo Lupe,barbi,Basso Ines,Benavides Negro,Benavides Rafa,Benitez Jesi,Benitez Yesi 2,Bernardini Cami,Biscaychipi Mariano,Boguetti Gonza,Bos Cata,Bos Yanina,Brondo Male,Bruno Mauro,Bustos Gimena,Cabrera Euge,Caloni Nico,Campana Marcela,Cano Marcela,Cañete Jose,Carusso Mia,Cassini Ro,Castro Nico,Cejas Vanesa,Centioli Mari,Conte Mariano,Coronel Sil,Cristian Loriega,Curci Juli,Curti Valentina,Dandrilli dani,Diaz Rosario,Diz Juli,Dominguez Vale,Dufayard ale,Dumanski Cristina,Echegaray Moni,Edu,Eggs Rocio,Erbacci Lujan,Espil Juli,Etchebere Mechi,Fardauz Lucas,Fernandez Graciela,Ferraz Oriana,Figiolo Fran,Figiolo Sol,Forni Anto,Furiati Ana,Gaitan Mariana,gallegos leo,Gamero rosana,Garau Lili,Garcia Cooper Jose,Gasparini Pilar,Geretto Curi,Giachino Mari luz,Gomez Nati,Gonzale Brian,Gonzalez Estefania,Gonzalez Fabi,Gorosito Vir,Guarino Valen,Haydee Scorzato,Hever Ceci,Ibarbuden Cami,Kuchta Agus,Kuchta Lara,laclotte carla,Laclotte May,Ledesma Matias,Lettiere Anto,Lombardo Nati,Lopez Lara,Lopez Sergio,Luccon igna,Luchetti vir,Luciaw Mari,Mancuso Tere,Marazzo Agos,Marczewuski Vale,Mariñelarena Zulma,Martin Flor,Martini Omar,Masino Sofi,Menendez Adriana,Miglioranza Cesar,Miglioranza Eva,Milito Vicky,Molinari Ceci,Morosini Blas,Negri Gaspar,Nicastro Monica,Nicosia Albert,Nievas Vir,Noriega Cristian,Oberti Marcelo,Oberti Valen,Orellano Caro,Pacheco Oli,Papaleo Cele,Parodi Coni,Parra Andres,Parra Diego,Pascarelli Marce,Paton Ana,Paz Lujan,Pellgrini Cami,Peña Cata,Peralta Jorgelina,Perez Mariana,Pisonero Mari,Platon Ana,Ponti Belen,Poza Luli,Poza Rodrigo,Priano Pau,Puyos Carla,Quevedo yani,Ravena Ana,Redondo Moni,Reynoso Vanesa,Rocha Daniel,Rocha Ricardo,Rodriguez Ana,Rodriguez Juli,Romanello Ceci,Rosso Marcela,Salinas Fausto,Salinas Pablo,Sanchez maria del carmen,Santiago Sil,Sartor Soledad,Scardulla Wendy,Scarnatto Marco,Segura Carlos,Sela Pablo,Silva Ana,Sinisi Nati,Solari Sofi,Somma Juli,Sosa Rosana,Soto Claudio,Spindola Gabriela,Suarez Santino,Tiberi Alberto,Tiberi Sergio,Tomas Pia,Torres Aldo (tobi),Torres Erica,Tourn Dalila,Valldosera Caro,Vigione Ana,Vilches Daniel,Vilches Estefnia,Vitale beto,Vitale Milagros,Zafalon Mica,Zeppa Delfi,Zeppa Ernes,Zeppa Vicky,Acosta Edu,Aggio Diego,Albornoz Marina,Alfano Ariel,Aliano Ana,Almacen Sil,Almada Aye,Alvarez Euge,Alvarez Sol,Amiguetti Pity,Amigutty jose,Amoros Santiago,Arroyo Celeste,Balumbo Lupe,Barbieri Pablo,Basso Ines,Benavidez Rafa,Benitez Jesi,Benitez Yesi 2,Bernardini Cami,Bisca Mariano,Boguetti Gonza,Bos Cata,Bos Yanina,Bosisio Barbi,Brondo Male,Bruno Mauro,Bustos Gimena,Cabrera Euge,Caloni Nico,Campana Marce,Cano Marcela,Cañete Jose,Carusso Mia,Cassini Ro,Cejas Vanesa,Centioli Mari,Charpertier Flor,Conte Mariano,Coronel Sil,Curci Juli,Curti Valentina,Dandrilli dani,Diaz Rosario,Diz Juli,Dominguez Valeria,Dufayard ale,Dumanski Cristina,Echegaray Moni,Eggs Rocio,Erbacci Lujan,Escobar Fran,Espin Juli,Etchebere Mechi,Fardauz Lucas,Fernandez Gabriela,Fernandez Graciela,Ferraz Oriana,Ferri Santi,Figliolo Fran,Figliolo sol,Forni Anto,Furiati Ana,Gaitan Mariana,Gamero rosana,Garcia Cooper Jose,Gasparini Pilar,Genari Cande,Geretto Curi,Giachino Mari luz,Gomes Marques Tefi,Gomez Diego,Gomez Nati,Gonzalez Brian,Gonzalez Fabi,Gorosito Vir,Guarino Valen,Haydee Scorzato,Henriksen Lara,Hever Ceci,Ibarbuden Cami,Laclotte May,Lacolotte Carla,Lettiere Anto,Lombardo Nati,Lopez Lari,Lopez Sergio,Luccon Jose,Luchetti vir,Luciaw Mari,Mancuso Tere,Marazzo Agos,Marczewuski Vale,Mariñelarena Zulma,Martin Flor,Martini Omar,Masino Sofi,Menendez Adriana,Miglioranza Cesar,Miglioranza Eva,Milito Vicky,Morosini Blas,Moyano Sofi,Negri Gaspar,Nicastro Monica,Nicastro Nico,Nicosia Albert,Nievas Vir,Nise Susana,Noriega Cristian,Oberti Marcelo,Orellano Ana,Orellano Caro,Oscavariz Juli,Otero Juli,Pacheco Oli,Papaleo Cele,Parodi Coni,Parra Andres,Parra Diego,Pascarelli Marce,Paz Lujan,Pellegrini Cami,Peña Cata,Peralta Jorgelina,Perez Mariana,Pisonero Mari,Platon Ana,Pomaroli ana,Ponti Maria Belen,Poza Luli,Poza Rodrigo,Priano Pau,Puyos Carla,Quevedo yani,Ravena Ana,Redondo Moni,Reynoso Vanesa,Rocha Daniel,Rocha Ricardo,Rodriguez Ana,Rodriguez Juli,Romanello Ceci,Rosso Marcela,Salinas Fausto,Salinas Pablo,Sanchez maria del carmen,Santiago Sil,Sartor Sole,Scarnatto Marco,Segura Carlos,Sela Pablo,Silva Ana,Sinisi Nati,Solari Sofia,Somma Juli,Sosa Rosana,Soto Claudio,Spindola Gabi,Thumak Vale,Tiberi Alberto,Tiberi Sergio,Tierno Pau,Tomas Pia,Torres Erica,Tourn Dalila,Valldosera Caro,Vigione Ana,Vilches Daniel,Vilches Estefania,Vitale Beto,Vitale Milagros,Zafalon Mica,Zeppa Delfi,Zeppa Ernes,Zeppa Vicky"

    socios_list = raw_users.split(',')

    socios_crear = []

    socios_vistos = set()  # Para evitar duplicados

    for user in socios_list:
        user = user.strip()
        if not user or user.lower() in socios_vistos:
            continue
        socios_vistos.add(user.lower())

        parts = user.split(' ', 1)
        if len(parts) == 2:
            apellido, nombre = parts
        else:
            apellido, nombre = parts[0], ''

        socios_crear.append(
            Socio(
                nombre=nombre.strip().capitalize(), 
                apellido=apellido.strip().capitalize(),
                dni=None,
                email=None,
                telefono=None
            )
        )

    Socio.objects.bulk_create(socios_crear)

class Migration(migrations.Migration):

    dependencies = [
        ('socios', '0002_alter_socio_dni_alter_socio_email_and_more'),
    ]

    operations = [
        migrations.RunPython(cargar_socios),
    ]

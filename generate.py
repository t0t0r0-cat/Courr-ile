import datetime
import gettext
import locale
import os
import subprocess
import sys
import warnings
from email.mime.text import MIMEText

from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

LANGUAGE = "fr"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

try:
  locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
except locale.Error:
  locale.setlocale(locale.LC_TIME, "")

translation = gettext.translation(
    "messages",
    localedir=os.path.join(BASE_DIR, "locales"),
    languages=[LANGUAGE],
    fallback=True
)


_ = translation.gettext

ACCEPT = {_("oui"), _("o")}
REFUSE = {_("non"), _("n")}

root = []
Edit = True
url=None
btn_text=None
texte=None
titre=None
def clean_input(prompt):
  value = input(prompt).strip()
  soup = BeautifulSoup(value, "html.parser")
  if not soup.find():
    return value
  warn_input = input(_("Cet entrée contient du html, voulez vous [R]etirer le contenu html, [e]diter votre entrée, [c]ontinuer avec le contenu html (risqué! peut produire des resultats inatendus) :\n> ")).strip().lower()
  if warn_input == _("e"):
    value = clean_input(prompt)
    return value
  elif warn_input == _("c"):
    print(_("Entrée sauvgardée dangereusement!"))
    return value
  else:
    value = soup.get_text()
    return value

def warn_input(prompt):
  answer = None
  while answer not in ACCEPT | REFUSE:
    answer = input(_("%s Oui/Non\n> ") % (prompt))
    if answer not in ACCEPT | REFUSE:
      print(_("Choix invalide."))
  return answer in ACCEPT

story_base=(f"""
    <div id="StoryPadding">
    <div id="Story">
      <h2>{titre}</h2>
    <hr />
    <p>{texte}</p>
    </div>
    </div>
""")

while Edit:
    print(_(
        "1 - Ajouter un article\n"
        "2 - Ajouter du texte supplémentaire\n"
        "3 - Sauvegarder"
    ))

    mode = input("> ").strip()

    if mode == "1":
        article = {}

        if warn_input(_("Ajouter un bouton ?")):
          article["url"] = clean_input(_("URL du bouton : "))
          while not article["url"].startswith(("https://", "http://")):
            prompt = input(_("Les liens devraient etre préfixés par `http://` ou `https://`. [C]orrigez cela vous-même, ou tapez [I]gnorer pour ignorer (Pas recomendé, les boutons ne fonctionneront pas!)\n> ")).strip().lower()
            if prompt == _("c"):
              article["url"] = clean_input(_("URL du bouton : "))
            else:
              if prompt == _("i"):
                break
              print(_("Choix invalide."))
          article["btn_text"] = clean_input(_("Texte du bouton : "))
          article["type"] = "story_btn"
        else:
            article["type"] = "story_base"
        article["titre"] = clean_input(_("Titre de l'article : "))
        article["texte"] = clean_input(_("Texte de l'article : "))
        root.append(article)

    elif mode == "2":
      texte_supplementaire = clean_input(_(
          "Texte supplémentaire : "
      )).strip()
      article = {
          "type": "texte_supplementaire",
          "texte": texte_supplementaire,
      }
      root.append(article)
    

    elif mode == "3":
        print(_("Sauvegarde..."))
        # Add your save code here
        Edit = False
    else:
        print(_("Choix invalide."))



prelude="""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
      @media screen and (min-width: 200px) and (max-width: 400px) {
        img { display: none; }
    }

    @media screen {
      * {
        font-size   : 12px;
        background-color: #EDC9FF;
        text-align: center;
      }
    }

    a {
      text-decoration: none;
    }

    p {
      font-size: 120%;
      color: #874392;
    }

    #Story p{
      background-color: #B98DE1;
      color: white;
    }

    h1 {
      font-size: xx-large;
      text-align: center;
      color: #874392;
    }

    h2 {
      font-size: medium;
    }

    #Story h2 {
      background-color: #B98DE1;
      color: white;
    }

    #Story {
      background-color: #B98DE1;
      padding: 1%;
      border-radius: 2%;
    }

    #StoryPadding {
      padding-bottom: 5%;
      padding-left: 2%;
      padding-right: 2%;
    }

    #CtaBtn {
      text-decoration: none;
      border-radius: 2.5%;
      background-color: #9A66D5;
      color: #DFA952;
      text-align: center;
      padding-top: 3%;
      padding-bottom: 3%;
      //transition: transform 0.2s ease;
    }

    /*#CtaBtn:hover {*/
    /*  text-decoration: none;*/
    /*  background-color: #B370BD;*/
    /*  color: #FFC849;*/
    /*  transform: scale(1.05);*/
    /*}*/

    #CtaBtnPadding {
      background-color: #B98DE1;
    }

    @media print {
      p {
        font-family : garamond, serif;
        font-size : 10px;
      }
        img {
        display:none
      }
    }

    /* For smart phones */
    @media screen and (max-width: 600px) {
    }

    /* For tablets */
    @media screen and (min-width: 600px) and (max-width: 900px) {
    }

    /* For desktop computers */
    @media screen and (min-width: 900px) {
    } 

    /* Device dimensions */
    @media screen and (max-device-height: 600px) {
    }

    /* Device orientation */
    @media screen and (orientation: portrait) {
    }

    /* Device aspect ratio */
    @media screen and (device-aspect-ratio: 16/9) {
    } 
    </style>

    <meta name="viewport" content="width=device-width, initial-scale=1"> 
    </head>

    <body>
      <header>
        <h1>Courr-Île</h1>
        <p>l'infolettre pour les eleves, par les eleves</p>
      </header>
"""

file = prelude

for i in range(len(root)):
  texte = root[i]["texte"]
  titre = root[i].get("titre", "")
  url = root[i].get("url", "")
  btn_text = root[i].get("btn_text", "")
  story_btn=(f"""  
      <div id="StoryPadding">
    <div id="Story">
        <h2>{titre}</h2>
        <hr />
        <p>{texte}</p>

        <a id="CtaBtn"
           href="{url}"
           style="
               display: inline-block;
               text-decoration: none;
               border-radius: 2.5%;
               background-color: #9A66D5;
               color: #DFA952;
               text-align: center;
               padding: 12px 30px;
           ">
            {btn_text}
        </a>

    </div>
</div>
    """)
  story_base=(f"""

      <div id="StoryPadding">
      <div id="Story">
        <h2>{titre}</h2>
      <hr />
      <p>{texte}</p>
      </div>
      </div>
  """)

renderers = {
    "story_base": lambda story_base=story_base: story_base,
    "story_btn": lambda story_btn=story_btn: story_btn,
    "texte_supplementaire": lambda texte=texte: f"<p>{texte}</p>",
}

article_type = root[i]["type"]
rendered_article = renderers[article_type]()
file += rendered_article


file += """
</body>
</html>
          """
print(_("copying html to clipboard"))
date = datetime.datetime.now()
filename = f"courr-ile-{date.strftime('%Y-%m-%d')}.html"
filename_eml = f"courr-ile-{date.strftime('%Y-%m-%d')}.eml"
try:
  with open(filename, "x") as f:
    f.write(file)
    print(_("Fichier HTML sauvgardé dans %s") % (filename))
except FileExistsError:
  if warn_input(_("Le fichier %s exsiste déjà. Voulez-vous le remplacer?") % (filename)):
    with open(filename, "w") as f:
      f.write(file)
      print(_("Fichier HTML sauvgardé dans %s") % (filename))
  else:
    print(_("Sauvgarde annulée."))

msg = MIMEText(file)
msg['Subject'] = (f"Courr-Île du {date.strftime("%d %B")}")

try:
  with open(filename_eml, "x") as f:
    f.write(msg.as_string())
    print(_("Fichier .eml sauvgardé dans %s") % (filename_eml))
except FileExistsError:
  if warn_input(_("Le fichier %s exsiste déjà. Voulez-vous le remplacer?") % (filename_eml)):
    with open(filename_eml, "w") as f:
        f.write(msg.as_string())  
        print(_("Fichier .eml sauvgardé dans %s") % (filename_eml))
  else:
    print(_("Sauvgarde annulée."))

print(_("Ouverture du fichier..."))
try:
    if os.path.exists(filename_eml):
        eml_path = os.path.abspath(filename_eml)
        if hasattr(os, "startfile"):
            os.startfile(eml_path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", eml_path])
        else:
            subprocess.Popen(["xdg-open", eml_path])
except FileNotFoundError:
   print(_("Ouvrez le fichier %s car l'ouverture automatique du fichier a echoué.") % (filename_eml))
print(_("Selectionnez réenvoyer ce message."))
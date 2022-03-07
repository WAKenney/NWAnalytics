import pandas as pd
import streamlit as st
sppColors = pd.read_excel(r"C:\Users\HP\Desktop\colorsTEMP.xlsx")

sppColors.set_index('species', drop=True, inplace=True)

st.write(sppColors)

sppC = sppColors.to_dict('dict')

st.write(sppC)

colorsDict = {"aldeur":"aliceblue","aldspe":" antiquewhite","aldspp":" aqua","aldwhi":" aquamarine","amumak":" azure",
    "appcom":" beige","appcra":" bisque","appspp":" black","aprico":" blanchedalmond","ashbla":" blue","ashblu":" blueviolet",
    "asheur":" brown","ashgre":" burlywood","ashman":" cadetblue","ashspp":" chartreuse","ashwhi":" chocolate",
    "asplar":" coral","asptre":" cornflowerblue","basswo":" cornsilk","beeame":" crimson","beeblu":" cyan","beeeur":" darkblue",
    "beespp":" darkcyan","birala":" darkgoldenrod","birche":" darkgray","bireur":" darkgrey","birgra":" darkgreen",
    "birhim":" darkkhaki","birriv":" darkmagenta","birspp":" darkolivegreen","birwhi":" darkorange","biryel":" darkorchid",
    "buceur":" darkred","bucohi":" darksalmon","bucred":" darkseagreen","bucspp":" darkslateblue","bucswe":" darkslategray",
    "bucyel":" darkslategrey","buhspp":" darkturquoise","butter":" darkviolet","catchi":" deeppink","catnor":" deepskyblue",
    "catsou":" dimgray","catspp":" dimgrey","cedjap":" dodgerblue","cedori":" firebrick","cedred":" floralwhite",
    "cedspp":" forestgreen","cedwes":" fuchsia","cedwhi":" gainsboro","cedyel":" ghostwhite","cheame":" gold","chebla":" goldenrod",
    "chechi":" gray","checho":" grey","cheeur":" green","chefru":" greenyellow","chehug":" honeydew","cheori":" hotpink",
    "chepin":" indianred","chepur":" indigo","chesar":" ivory","chespp":" khaki","cnutspp":" lavender","cofken":" lavenderblush",
    "coramu":" lawngreen","coteas":" lemonchiffon","crajap":" lightblue","crawil":" lightcoral","cucumb":" lightcyan","dead":" lightgoldenrodyellow",
    "devils":" lightgray","dogalt":" lightgrey","dogchi":" lightgreen","dogcor":" lightpink","dogflo":" lightsalmon","doggra":" lightseagreen",
    "dogred":" lightskyblue","dogspp":" lightslategray","eldspp":" lightslategrey","elmame":" lightsteelblue","elmcam":" lightyellow",
    "elmchi":" lime","elmdut":" limegreen","elmeng":" linen","elmjer":" magenta","elmroc":" maroon","elmsco":" mediumaquamarine",
    "elmsib":" mediumblue","elmsli":" mediumorchid","elmspp":" mediumpurple","euoeur":" mediumseagreen","euospp":" mediumslateblue",
    "firbal":" mediumspringgreen","firdou":" mediumturquoise","firfra":" mediumvioletred","firgra":" midnightblue","firspp":" mintcream",
    "firwhi":" mistyrose","flodou":" moccasin","forest":" navajowhite","ginkgo":" navy","golcha":" oldlace","gumbla":" olive",
    "hacber":" olivedrab","hawcoc":" orange","hawdow":" orangered","haweng":" orchid","hawlav":" palegoldenrod","hawsca":" palegreen",
    "hawsin":" paleturquoise","hawspp":" palevioletred","haznut":" papayawhip","haztur":" peachpuff","hazwit":" peru","hedge":" pink",
    "hemeas":" plum","hicbit":" powderblue","hicpig":" purple","hicsha":" red","hicshe":" rosybrown","hicspp":" royalblue","holly":" saddlebrown",
    "honfly":" salmon","honspp":" sandybrown","hoptre":" seagreen","horcom":" seashell","horeur":" sienna","horred":" silver",
    "horspp":" skyblue","hybpop":" slateblue","ironwo":" slategray","jappag":" slategrey","junchi":" snow","juncom":" springgreen",
    "juncre":" steelblue","junsav":" tan","junspp":" teal","kalopa":" thistle","katsur":" tomato","lareuo":" turquoise","larjap":" violet",
    "larspp":" wheat","lilcom":" yellow","liljap":" yellowgreen","lilspp":" yellow","linbig":" yellowgreen","lineur":"aliceblue",
    "linhyb":" antiquewhite","linlit":" aqua","linsil":" aquamarine","linspp":" azure","locbla":" beige","lochon":" bisque",
    "magsau":" black","magspp":" blanchedalmond","magsta":" blue","magumb":" blueviolet","mapamu":" brown","mapbla":" burlywood",
    "mapfre":" cadetblue","maphed":" chartreuse","mapjap":" chocolate","mapman":" coral","mapmou":" cornflowerblue",
    "mapnor":" cornsilk","mappap":" crimson","mapred":" cyan","mapsil":" darkblue","mapspp":" darkcyan","mapstr":" darkgoldenrod",
    "mapsug":" darkgray","mapsyc":" darkgrey","maptat":" darkgreen","mouame":" darkkhaki","mouchi":" darkmagenta","moucut":" darkolivegreen",
    "moueur":" darkorange","mouhyb":" darkorchid","moukor":" darkred","mousho":" darksalmon","mouspp":" darkseagreen","mouwhi":" darkslateblue",
    "mulbla":" darkslategray","mulred":" darkslategrey","mulspp":" darkturquoise","mulwhi":" darkviolet","nannyb":" deeppink","oakbla":" deepskyblue",
    "oakbur":" dimgray","oakchi":" dimgrey","oakeng":" dodgerblue","oakgar":" firebrick","oakhil":" floralwhite","oakmou":" forestgreen",
    "oakpin":" fuchsia","oakred":" gainsboro","oaksca":" ghostwhite","oakshi":" gold","oakshu":" goldenrod","oakspp":" gray",
    "oakswa":" grey","oakwhi":" green","olirus":" greenyellow","oraosa":" honeydew","paulon":" hotpink","pawpaw":" indianred",
    "peachs":" indigo","peacom":" ivory","peaflo":" khaki","peahar":" lavender","peapea":" lavenderblush","peawee":" lawngreen",
    "persim":" lemonchiffon","pinaus":" lightblue","pinbri":" lightcoral","pinhim":" lightcyan","pinjac":" lightgoldenrodyellow",
    "pinlob":" lightgray","pinmug":" lightgrey","pinpit":" lightgreen","pinpon":" lightpink","pinred":" lightsalmon","pinsco":" lightseagreen",
    "pinspp":" lightskyblue","pinwes":" lightslategray","pinwhi":" lightslategrey","plalon":" lightsteelblue","plaspp":" lightyellow",
    "pluame":" lime","plucan":" limegreen","plumyr":" linen","poorce":" magenta","popbal":" maroon","popbla":" mediumaquamarine",
    "popcar":" mediumblue","popspp":" mediumorchid","popwhi":" mediumpurple","pruspp":" mediumseagreen","raintr":" mediumslateblue",
    "redbud":" mediumspringgreen","reddaw":" mediumturquoise","redwoo":" mediumvioletred","rose":" midnightblue","rossha":" mintcream",
    "sassaf":" mistyrose","serdow":" moccasin","sersmo":" navajowhite","serspp":" navy","servic":" oldlace","silcar":" olive",
    "smotre":" olivedrab","snag":" orange","sprbla":" orangered","sprblu":" orchid","spreng":" palegoldenrod","sprnor":" palegreen",
    "sprred":" paleturquoise","sprser":" palevioletred","sprspp":" papayawhip","sprwhi":" peachpuff","stump":" peru","sumacs":" pink",
    "sumspp":" plum","sweetg":" powderblue","sycame":" purple","tamara":" red","treeof":" rosybrown","tulipt":" royalblue","unknow":" saddlebrown",
    "vibspp":" salmon","walbla":" sandybrown","waleng":" seagreen","walman":" seashell","walspp":" sienna","wayfar":" silver","werece":" skyblue",
    "whiswe":" slateblue","wilarc":" slategray","wilbay":" slategrey","wilbeb":" snow","wilbla":" springgreen","wilcor":" steelblue",
    "wilcra":" tan","wilfal":" teal","wilgoa":" thistle","wilpea":" tomato","wilpus":" turquoise","wilshi":" violet","wilspp":" wheat",
    "wilwee":" yellow","wilwhi":" yellowgreen","wingnu":" yellow","x":" yellowgreen","yellow":"aliceblue","yewcom":" antiquewhite",
    "yeweur":" aqua","yewjap":" aquamarine","yewspp":" azure","zeljap":" beige","other":"gray"}

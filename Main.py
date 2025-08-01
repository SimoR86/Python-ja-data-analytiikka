# -*- coding: utf-8 -*-
"""
Created on Tue Jul  8 09:49:25 2025

@author: Simo Ruotsalainen
"""

import requests
import json
from pyjstat import pyjstat
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import mannwhitneyu
import plotly.express as px

"""
https://thl.fi/tilastot-ja-data/tilastot-aiheittain/sosiaali-ja-terveydenhuollon-resurssit/terveydenhuollon-menot-ja-rahoitus
https://thl.fi/tilastot-ja-data/tilastot-aiheittain/ikaantyneet/kotihoito
https://sampo.thl.fi/pivot/prod/fi/avo/perus11/summary_kotih1102?sukupuoli_0=11936&ikaluokka_0=446200&saannollisyys_0=369&kotihstatus_0=446224&intensiivisyys_0=446226&kayntitaajuus_0=460922&kesto_0=383&mittari_0=87454#
https://pxdata.stat.fi/PxWeb/pxweb/fi/StatFin/StatFin__vaerak/statfin_vaerak_pxt_11re.px/table/tableViewLayout1/
https://github.com/varmais/maakunnat/blob/master/maakunnat.geojson

Before running this code, make sure you have already installed all the required libraries. 
Some visualizations will open in a browser window and will be saved to your hard drive as HTML files VIA Plotly. 
If you don't want to save anything to your hard drive, please remove lines 103, 113, 139 & 605 from Main.py
"""

# Funktio hakee annetusta URLsta JSON-kyselyllä (Tilastokeskuksen PxWeb)
def datahaku(url, query):
    
    headers = {"Content-Type": "application/json"}
    
    try:
        print("Lähetetään kysely")
        response = requests.post(url, headers=headers, data=json.dumps(query))
        
        print(f"Status: {response.status_code}")
        response.raise_for_status()
        
        """
        Status codes (error messages):
        200 - OK
        404 - errors in syntax of the query or POST URL not found.
        403 - blocking when querying for large data sets. The API limit is now 100,000 cells.
        429 - Too many queries within a minute. The API limit is now 30 queries within 10 seconds.
        503 - Time-out after 60 seconds. It may turn on, when extracting large XLSX datasets. 
                  (We do not recommend that).
        """
        
        if response.status_code == 200:
            print("OK")
        elif response.status_code == 404:
            print("errors in syntax of the query or POST URL not found.")
        elif response.status_code == 403:
            print("blocking when querying for large data sets. The API limit is now 100,000 cells.")
        elif response.status_code == 429:
            print("Too many queries within a minute. The API limit is now 30 queries within 10 seconds.")
        else:
            print("Time-out after 60 seconds. It may turn on, when extracting large XLSX datasets.")
        
        data = response.json()
        print("Data vastaanotettu")
        
        if not data:
            print("API ei palauttanut dataa")
            return None
        
        data = json.dumps(data)
        
        dataset = pyjstat.Dataset.read(data)
        
        df = dataset.write("dataframe")
        
        
        return df
    
    except requests.exceptions.RequestException as e:
        print(f"Virhe haettaessa dataa:\n{e}")
        return None
    
def line(df, x, y, hue, title):  
    fig = px.line(df,
                  x=x,
                  y=y,
                  color=hue,
                  line_group=hue,
                  hover_name=hue,
                  markers=True,
                  labels={x:x,y:y,hue:hue},
                  title=title
                  )

    fig.update_layout(
        height=600,
        xaxis_title=x,
        yaxis_title=y,
        legend_title=hue,
        template="plotly_white"
        )
    
    fig.show(renderer="browser")
    fig.write_html(f"{title}.html")

def pie(df, values, names, title):
    fig = px.pie(df,
                 values=values,
                 names=names,
                 title=title
                 )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.show(renderer="browser")
    fig.write_html(f"{title}.html")
    
def bar(df, x, y, color, title, animation_frame):
    if pd.api.types.is_numeric_dtype(df[x]):
        text_value = x
    else:
        text_value = y
    fig = px.bar(df,
                 x=x,
                 y=y,
                 color=color,
                 animation_frame=animation_frame,
                 title=title,
                 text=text_value                      
                 )
    fig.update_traces(textposition="inside")
    
    fig.update_layout(
        height=1200,
        xaxis_title=x,
        yaxis_title=y,
        legend_title=color,
        template="plotly_white"
        )
    
    fig.show(renderer="browser")
    fig.write_html(f"{title}.html")    

def lineplt(df, xakseli, yakseli, hue, title):

    plt.figure(figsize=(16,8))

    sns.lineplot(data=df, x=xakseli, y=yakseli, hue=hue, marker = "o")
    plt.title(title)
    plt.xlabel(xakseli)
    plt.ylabel(yakseli)
    plt.legend(title=hue, loc="lower left")
    plt.xticks(rotation=60)
    plt.grid(True)
    
    plt.show()
    
# Riippuvuudet hajontakaaviona    
def riippuvuudet(df):
    plt.figure(figsize=(26,26))
    sns.pairplot(df, kind="reg")
    plt.show()
    
    

def heatmap(df):
    plt.figure(figsize=(26,12))
    
    correlation_matrix = df.corr().round(2)
    
    r2_matrix = (df.corr() ** 2).round(2)
    
    plt.subplot(1, 2, 1)
    sns.heatmap(data=correlation_matrix, annot=True, cmap="coolwarm", vmin=-1, vmax=1)
    plt.title("Pearsonin korrelaatiokertoimet (r)")

    # R²
    plt.subplot(1, 2, 2)
    sns.heatmap(data=r2_matrix, annot=True, cmap="YlGnBu", vmin=0, vmax=1)
    plt.title("Selitysasteet (R²)")
    plt.show()
    
# Haetaan tietolähteet tilastokeskuksen PxWeb-rajapinnasta käyttämällä "datahaku"-funktiota
url = "https://pxdata.stat.fi:443/PxWeb/api/v1/fi/StatFin/eot/statfin_eot_pxt_11ze.px"
query = {
  "query": [
    {
      "code": "Ikä",
      "selection": {
        "filter": "item",
        "values": [
          "16-24",
          "25-34",
          "35-49",
          "50-64",
          "65-74",
          "75-84",
          "85-"
        ]
      }
    },
    {
      "code": "Itse koettu terveydentila",
      "selection": {
        "filter": "item",
        "values": [
          "1",
          "2",
          "3",
          "6"
        ]
      }
    }
  ],
  "response": {
    "format": "json-stat2"
  }
}

tyytyvaisyys = datahaku(url, query)

url1 = "https://pxdata.stat.fi:443/PxWeb/api/v1/fi/StatFin/eot/statfin_eot_pxt_13xi.px"
query1 = {
  "query": [],
  "response": {
    "format": "json-stat2"
  }
}

toimintarajoitteiset = datahaku(url1, query1)

url2 = "https://pxdata.stat.fi:443/PxWeb/api/v1/fi/StatFin/eot/statfin_eot_pxt_13xj.px"
query2 = {
  "query": [
    {
      "code": "Ikä",
      "selection": {
        "filter": "item",
        "values": [
          "SSS",
          "16-34",
          "35-49",
          "50-64",
          "65-74",
          "75-"
        ]
      }
    }
  ],
  "response": {
    "format": "json-stat2"
  }
}

toimintarajoitteet = datahaku(url2, query2)

url3 = "https://pxdata.stat.fi:443/PxWeb/api/v1/fi/StatFin/eot/statfin_eot_pxt_11z9.px"
query3 = {
  "query": [
    {
      "code": "Ikä",
      "selection": {
        "filter": "item",
        "values": [
          "SSS",
          "16-24",
          "25-34",
          "35-49",
          "50-64",
          "65-74",
          "75-84",
          "85-"
        ]
      }
    },
    {
      "code": "Yksinäinen",
      "selection": {
        "filter": "item",
        "values": [
          "12",
          "20"
        ]
      }
    }
  ],
  "response": {
    "format": "json-stat2"
  }
}

yksinaisyys = datahaku(url3, query3)

url4 = "https://pxdata.stat.fi:443/PxWeb/api/v1/fi/StatFin/sutivi/statfin_sutivi_pxt_13ud.px"
query4 = {
  "query": [
    {
      "code": "Sukupuoli",
      "selection": {
        "filter": "item",
        "values": [
          "SSS"
        ]
      }
    },
    {
      "code": "Ikä",
      "selection": {
        "filter": "item",
        "values": [
          "1",
          "2",
          "3",
          "4",
          "5",
          "6",
          "7"
        ]
      }
    },
    {
      "code": "Tiedot",
      "selection": {
        "filter": "item",
        "values": [
          "mphtss",
          "iot_dva",
          "iuph1a",
          "iuph1b",
          "iuchat1",
          "iuif",
          "ihif",
          "iubk",
          "iunw",
          "iusell",
          "iusnet1",
          "iusnetf1",
          "igovip",
          "igovapro",
          "ibuy1",
          "ibuy2",
          "bclot1",
          "bfdr",
          "bhlfts",
          "bhlfts1",
          "bapp",
          "bctick",
          "bsutil",
          "btps_e",
          "bots",
          "iug_dtv",
          "ieid1",
          "ieid2",
          "ieid3"
        ]
      }
    }
  ],
  "response": {
    "format": "json-stat2"
  }
}

tekniikka = datahaku(url4, query4)

url5 ="https://pxdata.stat.fi:443/PxWeb/api/v1/fi/StatFin/vaerak/statfin_vaerak_pxt_11re.px"
query5 = {
  "query": [
    {
      "code": "Alue",
      "selection": {
        "filter": "agg:_Maakunnat 2025.agg",
        "values": [
          "MK01",
          "MK02",
          "MK04",
          "MK05",
          "MK06",
          "MK07",
          "MK08",
          "MK09",
          "MK10",
          "MK11",
          "MK12",
          "MK13",
          "MK14",
          "MK15",
          "MK16",
          "MK17",
          "MK18",
          "MK19",
          "MK21"
        ]
      }
    },
    {
      "code": "Ikä",
      "selection": {
        "filter": "agg:Ikäkausi 0-14, 15-24, 25-44, 45-64, 65-.agg",
        "values": [
          "SSS",
          "65-"
        ]
      }
    },
    {
      "code": "Sukupuoli",
      "selection": {
        "filter": "item",
        "values": [
          "SSS"
        ]
      }
    }
  ],
  "response": {
    "format": "json-stat2"
  }
}

vaesto = datahaku(url5, query5)

url6 = "https://pxdata.stat.fi:443/PxWeb/api/v1/fi/StatFin/vaerak/statfin_vaerak_pxt_11ra.px"
query6 = {
  "query": [
    {
      "code": "Alue",
      "selection": {
        "filter": "agg:_- Maakunnat 2025.agg",
        "values": [
          "SSS",
          "MK01",
          "MK02",
          "MK04",
          "MK05",
          "MK06",
          "MK07",
          "MK08",
          "MK09",
          "MK10",
          "MK11",
          "MK12",
          "MK13",
          "MK14",
          "MK15",
          "MK16",
          "MK17",
          "MK18",
          "MK19",
          "MK21"
        ]
      }
    },
    {
      "code": "Tiedot",
      "selection": {
        "filter": "item",
        "values": [
          "vaesto_yli64_p"
        ]
      }
    }
  ],
  "response": {
    "format": "json-stat2"
  }
}

ikaantyneet = datahaku(url6, query6)



# Haetaan tiedot Excel-tiedostoista
bktoecd = pd.read_excel("Menot_ja_rahoitus.xlsx", sheet_name = "Taulukko 8")

ikaantyneidenpalvelut = pd.read_excel("Menot_ja_rahoitus.xlsx", sheet_name = "Taulukko 4b")

palvelutME = pd.read_excel("Menot_ja_rahoitus.xlsx", sheet_name = "Taulukko 4a")

kh_asiakkaat = pd.read_excel("KH_asiakkaat_maakunnittain.xlsx")

# Siivotaan data: poistetaan tyhjät rivit, muutetaan tietotyypit, muutetaan sarakeotsikot sekä
# tehdään tarvittavat toimenpiteet laskennan mahdollistamiseksi seuraavista tietolähteistä:
    
# Kotihoidon asiakkaat
kh_asiakkaat.dropna(inplace=True)
kh_asiakkaat = kh_asiakkaat.drop(index=[0, 24, 25, 26]).reset_index(drop=True) 
vuodet = [str(v) for v in range(2014, 2024)]
kh_asiakkaat[vuodet] = kh_asiakkaat[vuodet].astype(int)                                   
kh_asiakkaat = kh_asiakkaat.rename(columns={"Avohilmo: Kotihoidon asiakkaat" : "Maakunta"})
kh_asiakkaat = kh_asiakkaat.melt(id_vars="Maakunta", var_name="Vuosi", value_name="Arvo")
kh_asiakkaat["Vuosi"] = kh_asiakkaat["Vuosi"].astype(int)

# Käyttömenot suhteessa BKT:een OECD-maissa
bktoecd.columns = bktoecd.iloc[1]
bktoecd = bktoecd.drop(index=[1]).reset_index(drop=True)
bktoecd.dropna(inplace=True)
bktoecd.columns = ["Maa"] + [vuosi for vuosi in range(2000, 2023)]

# Ikääntyneiden palvelujen menojen rakenne 2000-2022 %
ikaantyneidenpalvelut.columns = ikaantyneidenpalvelut.iloc[1]
ikaantyneidenpalvelut = ikaantyneidenpalvelut.drop(index=[1]).reset_index(drop=True)
ikaantyneidenpalvelut.dropna(inplace=True)
ikaantyneidenpalvelut.columns = ["Toiminto"] + [vuosi for vuosi in range(2000, 2023)]

# Ikääntyneiden palvelujen menojen rakenne 2000-2022 M€
palvelutME.columns = palvelutME.iloc[1]
palvelutME = palvelutME.drop(index=[1]).reset_index(drop=True)
palvelutME.dropna(inplace=True)
palvelutME.columns = ["Toiminto"] + [vuosi for vuosi in range(2000, 2023)]

# Yksinäisyyden tunne neljän viikon aikana 16 vuotta täyttäneessä väestössä vuosittain
yksinaisyys = pd.pivot_table(yksinaisyys, index= ["Ikä", "Vuosi", "Yksinäinen"], columns= "Tiedot",values = "value" ).reset_index()
yksinaisyys["Vuosi"] = yksinaisyys["Vuosi"].astype(int)

# Väestön tieto- ja viestintätekniikan käytön kehitys 2000-2024
tekniikka = pd.pivot_table(tekniikka, index=["Vuosi", "Ikä"], columns="Tiedot", values="value").reset_index()
tekniikka = tekniikka.fillna(0)
tekniikka["Vuosi"] = tekniikka["Vuosi"].astype(int)

# Väestörakenteen kehitys ikäryhmittäin ja maakunnittain
vaesto = vaesto[["Alue", "Ikä", "Vuosi", "value"]] 
vaesto["Vuosi"] = vaesto["Vuosi"].astype(int)
vaesto["Alue"] = vaesto["Alue"].str.replace(r"^MK\d+\s+"," ", regex=True)

# Toimintarajoitteiset 2022
toimintarajoitteiset = pd.pivot_table(toimintarajoitteiset, index=["Sukupuoli","Ikä"], columns="Tiedot", values="value").reset_index()
toimintarajoitteiset = toimintarajoitteiset.fillna(0)

# Toimintarajoitteet 2022
toimintarajoitteet = pd.pivot_table(toimintarajoitteet, index=["Ikä", "Toimintarajoitteen aste"], columns="Tiedot", values="value").reset_index()
toimintarajoitteet = toimintarajoitteet.fillna(0)

# Ikääntyneiden osuus
ikaantyneet["Vuosi"] = ikaantyneet["Vuosi"].astype(int)
ikaantyneet_kokomaa = ikaantyneet[ikaantyneet["Alue"] == "KOKO MAA"]
ikaantyneet_MK = ikaantyneet[ikaantyneet["Alue"] != "KOKO MAA"]
ikaantyneet_MK["Alue"] = ikaantyneet_MK["Alue"].str.replace(r"^MK\d+\s+"," ", regex=True)
ikaantyneet_MK["Alue"] = ikaantyneet_MK["Alue"].str.strip()

# Tyytyväisyys
tyytyvaisyys["value"] = tyytyvaisyys["value"].fillna(0)
tyytyvaisyys["Vuosi"] = tyytyvaisyys["Vuosi"].astype(int)

# muunnetaan leveä taulukko pitkään muotoon terveydenhuollon käyttömenojen osuuksista bruttokansantuotteesta OECD-maissa
bktoecd_melted = bktoecd.melt(id_vars="Maa", var_name="Vuosi", value_name="% bruttokansantuotteesta")
bktoecd_melted["Vuosi"] = bktoecd_melted["Vuosi"].astype(int)

# Terveydenhuollon käyttömenot vuosittain OECD-maissa lineplot
line(bktoecd_melted, "Vuosi", "% bruttokansantuotteesta", "Maa", "Terveydenhuollon käyttömenot vuosittain OECD-maissa")

# Suodatetaan väestön kokonaismäärä 
vaestosum = vaesto[vaesto["Ikä"] == "Yhteensä"]

# Suodatetaan yli 65-vuotiaat maakunnittain
vanhat = vaesto[vaesto["Ikä"] == "65 -"]

# Piirretään interaktiivinen ja animoitu viivakaavio väestön kokonaiskehityksestä
line(vaestosum,"Vuosi", "value", "Alue", "Väestönkehitys maakunnittain")

# Piirretään interaktiivinen palkkikaavio terveydenhuollon käyttömenoista OECD-maissa vuosittain
bar(bktoecd_melted, "% bruttokansantuotteesta", "Maa", "Maa", "Terveydenhuollon käyttömenojen osuus bruttokansantuotteesta OECD-maissa", "Vuosi") 

# Piirretään interaktiivinen ja animoitu palkkikaavio väestön kokonaiskehityksestä 
bar(vaestosum, "value", "Alue", "Alue", "Väestönkehitys maakunnittain", "Vuosi")

# Piirretään interaktiivinen ja animoitu palkkikaavio yli 65-vuotiaden väestökehityksestä maakunnittain
bar(vanhat, "value", "Alue", "Alue", "Yli 65-vuotiaiden väestönkehitys maakunnittain", "Vuosi")

# Piirretään interaktiivinen ja animoitu palkkikaavio yli 65-vuotiaan väestön osuudesta koko maassa
bar(ikaantyneet_kokomaa, "value", "Alue", "Alue", "Yli 65-vuotiaiden osuus koko maassa vuosittain", "Vuosi")

# Piirretään interaktiivinen ja animoitu palkkikaavio yli 65-vuotiaan väestön osuudesta maakunnittain
bar(ikaantyneet_MK, "value", "Alue", "Alue", "Yli 65-vuotiaiden osuus maakunnittain ja vuosittain", "Vuosi")

# muunnetaan leveä taulukko pitkään muotoon väestön tieto- ja viestintätekniikan käytöstä eri vuosina
tekniikka_melted = tekniikka.melt(id_vars = ["Ikä", "Vuosi"], var_name= "Palvelu", value_name="Käyttäjien osuus")
tekniikka_melted = tekniikka_melted[
    ~tekniikka_melted["Palvelu"].isin([
        'Soittanut videopuheluja  viimeisen 3 kuukauden aikana, %',
        'Kirjautunut johonkin palveluun matkapuhelinoperaattorin mobiilivarmeenteella viimeisen 12 kuukauden aikana, %',
        'Kirjautunut johonkin palveluun verkkopankin tunnuksella tai mobiilitunnisteella viimeisen 12 kuukauden aikana, %'
    ])
]


# Piirretään interaktiivinen palkkikaavio väestön tieto- ja viestintätekniikan käytöstä vuosittain ja ikäryhmittäin
bar(tekniikka_melted, "Käyttäjien osuus", "Palvelu", "Ikä", "Ikäryhmien osuus tieto- ja viestintätekniikan käytössä vuosina 2013 - 2024", "Vuosi")

# Harjoitellaan paikkatietoaineistojen käyttämistä karttavisualisoinneissa. geojson-tiedosto ladattu osoitteesta: https://github.com/varmais/maakunnat/blob/master/maakunnat.geojson?short_path=81dbd20
# Ladataan tiedosto kansiosta
with open("maakunnat.geojson", encoding="utf-8") as f:
    geojson = json.load(f)

# Piirretään kartta ja käytetään maakunnan nimeä tunnisteena koordinaateille.   
    fig = px.choropleth(ikaantyneet_MK,
                        geojson=geojson,
                        locations="Alue",
                        featureidkey="properties.Maakunta",
                        color="value",
                        color_continuous_scale="Viridis",
                        projection="mercator",
                        title="Yli 65-vuotiaiden osuus väestöstä maakunnittain",
                        animation_frame="Vuosi"
                        )
    fig.update_geos(fitbounds="locations", visible=True)
    fig.show(renderer="browser")
    fig.write_html("Yli65Map.html")

# Piirretään palkkikaavio, jossa vertaillaan yksinäisyyden tunnetta väestössä vuosina 2018 ja 2022.
bar(yksinaisyys, "Ikä", "Henkilöiden osuus (%)", "Yksinäinen", "Yksinäisyyden tunne väestössä ikäryhmittäin vuosina 2018 ja 2022", "Vuosi")

# Muutetaan leveä taulukko pitkään muotoon, poistetaan turhat rivit, muutetaan tietotyypit ja pyöristetään sarakkeen tiedot kahden desimaalin tarkkuuteen
ikaantyneidenpalvelut_melted = ikaantyneidenpalvelut.melt(id_vars="Toiminto", var_name="Vuosi",value_name="Osuus ikääntyneiden palveluista (%)")
ikaantyneidenpalvelut_melted = ikaantyneidenpalvelut_melted[ikaantyneidenpalvelut_melted["Osuus ikääntyneiden palveluista (%)"] != 100]
ikaantyneidenpalvelut_melted["Vuosi"] = ikaantyneidenpalvelut_melted["Vuosi"].astype(int)
ikaantyneidenpalvelut_melted["Osuus ikääntyneiden palveluista (%)"] = ikaantyneidenpalvelut_melted["Osuus ikääntyneiden palveluista (%)"].map(lambda x: f"{x:.2f}")
ikaantyneidenpalvelut_melted["Osuus ikääntyneiden palveluista (%)"] = ikaantyneidenpalvelut_melted["Osuus ikääntyneiden palveluista (%)"].astype(float)

# Piirretään kaavio eri palveluiden osuuksista kokonaiskäyttömenoista vuosittain.
bar(ikaantyneidenpalvelut_melted,"Osuus ikääntyneiden palveluista (%)", "Toiminto", "Toiminto", "Ikääntyneiden palveluiden menojen rakenne vuosittain", "Vuosi" )

# Otetaan tarkasteluun toimintarajoitteisten osuudet ikäluokittain vuonna 2022 ja piirretään piirakkakaavio.
toimintarajoitteiset = toimintarajoitteiset[toimintarajoitteiset["Sukupuoli"] == "Yhteensä"]
pie(toimintarajoitteiset,"Toimintarajoitteisten osuus, %","Ikä", "Toimintarajoitteisten osuus ikäryhmittäin vuonna 2022")

# Tarkastellaan lähemmin tiettyjä toimintarajoitteiden osuuksia eri ikäryhmissä vuonna 2022 pylväskaavion avulla. 
# Muokataan dataframe piirtoystävälliseen muotoon ja piirretään pylväskaavio.
toimintarajoitteet = toimintarajoitteet[["Ikä", 
                                         "Toimintarajoitteen aste", 
                                         "Itsestä huolehtiminen, %", 
                                         "Kommunikointi, %", 
                                         "Kuuleminen, %", 
                                         "Käveleminen tai portaiden kulkeminen, %", 
                                         "Muistaminen tai keskittyminen, %", 
                                         "Näkeminen, %"]]
toimintarajoitteet_melted = toimintarajoitteet.melt(id_vars=["Ikä", "Toimintarajoitteen aste"], var_name="Toimintarajoite", value_name="Arvo")
bar(toimintarajoitteet_melted, "Toimintarajoite", "Arvo", "Toimintarajoitteen aste", "Toimintarajoitteet ikäryhmittäin vuonna 2022", "Ikä")

# Piirretään pylväskaavio elämään tyytyväisyyden kokemuksesta ikäryhmittäin ja vuosittain.
bar(tyytyvaisyys, "value", "Itse koettu terveydentila", "Ikä", "Koetun tyytyväisyyden keskiarvo (asteikolla 1-10, jossa 1 on erittäin tyytymätön ja 10 erittäin tyytyväinen) vuosittain itse koetun terveydentilan ja ikäryhmän perusteella", "Vuosi")

# Piirretään pylväskaavio kotihoidon asiakasmäärien kehityksestä maakunnittain
bar(kh_asiakkaat, "Arvo", "Maakunta", "Maakunta", "Kotihoidon asiakasmäärien kehitys maakunnittain vuosina 2014-2023", "Vuosi")

kh_asiakkaat_summa = kh_asiakkaat.groupby("Vuosi")["Arvo"].sum().reset_index()
kh_asiakkaat_summa = kh_asiakkaat_summa.rename(columns={"Arvo" : "Kotihoidon asiakasmäärät"})
ikaantyneet_kokomaa_14_23 = ikaantyneet_kokomaa[ikaantyneet_kokomaa["Vuosi"].between(2014, 2023)].reset_index()
ikaantyneet_kokomaa_14_23 = ikaantyneet_kokomaa_14_23.rename(columns={"value": "65-vuotta täyttäneiden osuus"})
kh_asiakkaat_ja_vaesto = pd.merge(ikaantyneet_kokomaa_14_23, kh_asiakkaat_summa, on= "Vuosi", how= "inner")
kh_asiakkaat_ja_vaesto = kh_asiakkaat_ja_vaesto[["Vuosi","65-vuotta täyttäneiden osuus", "Kotihoidon asiakasmäärät"]]

# Tutkitaan korrelaatioita kotihoidon asiakasmäärien kehityksen ja ikääntyneen väestön kehityksen välillä vuosina 2014 - 2023.
heatmap(kh_asiakkaat_ja_vaesto)

# Tutkitaan vuosia 2000-2022 ikääntyneen väestön ja kotihoidon menojen osalta. Yhdistetään taulukot vuosiluvun perusteella.
palvelut = ikaantyneidenpalvelut_melted[ikaantyneidenpalvelut_melted["Toiminto"] == "1.3 Kotipalvelut*"]
ikaantyneet_kokomaa_00_22 = ikaantyneet_kokomaa[ikaantyneet_kokomaa["Vuosi"].between(2000,2022)].reset_index()
kh_ja_ikaantyneet = pd.merge(palvelut, ikaantyneet_kokomaa_00_22, on="Vuosi", how="inner")
kh_ja_ikaantyneet = kh_ja_ikaantyneet.rename(columns={"value": "65-Vuotta täyttäneiden osuus"})
kh_ja_ikaantyneet = kh_ja_ikaantyneet[["Vuosi",
                                       "Osuus ikääntyneiden palveluista (%)",
                                       "65-Vuotta täyttäneiden osuus"]]
kh_ja_ikaantyneet = kh_ja_ikaantyneet.rename(columns={"Osuus ikääntyneiden palveluista (%)":"Ikääntyneiden palveluista (%)",
                                                      "65-Vuotta täyttäneiden osuus" : "Yli 65-vuotiaat"})

"""
Tutkitaan korrelaatiota ikääntyneiden palveluiden ja kotihoidon osuuksien kokonaiskäyttömenoista välillä.
Käytetään pairplotia ja heatmapia sujuvaan vertailuun. 

* Vuodesta 2015 alkaen toiminto 1.3 Kotipalvelut sisältää Kuntatalous -tilaston kotihoidon tehtäväluokan 
(sis. Kotihoidon,  kotipalvelut ja kotisairaanhoidon) kustannukset. Ikääntyneiden, vähintään 65-vuotiaat, 
menojen osuus on arvioitu Avohilmon käyntitiedoista käynnin ikätiedon perusteella. 
Vuosien 2000–2014 toiminto 1.3 Kotipalvelut sisältää aiemman kuntien ja kuntayhtymien talous - ja toiminta tilaston tehtäväluokan kotipalvelut kustannukset.
"""
riippuvuudet(kh_ja_ikaantyneet)
heatmap(kh_ja_ikaantyneet)

# Huomataan kuvista, että kotipalvelut sisältävät kotihoidon tehtäväluokan vasta vuodesta 2015.
# Tarkastellaan vuosia 2015 - 2022.

kh_ja_ikaantyneet = kh_ja_ikaantyneet[kh_ja_ikaantyneet["Vuosi"].between(2015, 2022)]

# Tarkastellaan korrelaatiota relevantilla aikavälillä
riippuvuudet(kh_ja_ikaantyneet)
heatmap(kh_ja_ikaantyneet)

# Tehdään mann-whitneyn u testi toimintarajoitteista, toimintarajoitteiden asteilla "ei vaikeuksia" ja "vähän vaikeuksia" eri ikäryhmien välillä.
# rajataan datasta pois ensin yhteenlasketut arvot ja jätetään rivit joissa toimintarajoitteena on itsestä huoletiminen.
"""
H0:
    Toimintarajoitteella ei ole vaikutusta toimintakykyyn
H1:
    Vähäiselläkin muutoksella toimintarajoitteessa on merkittäviä vaikutuksia toimintakykyyn
"""
toimintarajoitteet_melted_test_data = toimintarajoitteet_melted[(toimintarajoitteet_melted["Ikä"] != "Yhteensä") &
                                                                (toimintarajoitteet_melted["Toimintarajoite"] == "Itsestä huolehtiminen, %")]
toimintarajoitteet_melted_test_data = toimintarajoitteet_melted[toimintarajoitteet_melted["Toimintarajoite"] == "Itsestä huolehtiminen, %"]
ei_vaikeuksia = toimintarajoitteet_melted_test_data[toimintarajoitteet_melted_test_data["Toimintarajoitteen aste"] == "Ei vaikeuksia"]["Arvo"]
vahan_vaikeuksia = toimintarajoitteet_melted_test_data[toimintarajoitteet_melted_test_data["Toimintarajoitteen aste"] == "Vähän vaikeuksia"]["Arvo"]

stat, p_value = mannwhitneyu(ei_vaikeuksia, vahan_vaikeuksia, alternative="two-sided")
print(f"U = {stat:.2f}\np-arvo = {p_value:.4f}")

"""
U = 36.00
p-arvo = 0.0050

Tulos on tilastollisesti merkitsevä 5 % riskitasolla. Hylätään nollahypoteesi.
Tulos vahvistaa, että vähäisilläkin toimintarajoitteilla itsestä huolehtimisen osalta on vaikutusta toimintakykyyn
"""

# Tarkastellaan vielä ikääntyneiden palvelujen osuuksien kehitystä terveydenhuollon kokonaiskäyttömenoista.
# Luetaan työkirjan ensimmäinen taulukko, muutetaan sarakeotsikot, suodatetaan kokonaismenot, muutetaan taulukko pitkään muotoon,
# yhdistetään taulukot vuoden perusteella ja lasketaan prosenttiosuudet euromääräisistä arvoista uuteen sarakkeeseen.
# Piirretään palkkikaavio
kokonaismenot = pd.read_excel("Menot_ja_rahoitus.xlsx", sheet_name = "Taulukko 1")
kokonaismenot.columns = kokonaismenot.iloc[1]
kokonaismenot = kokonaismenot[kokonaismenot["Toiminto"] == 'Terveydenhuoltomenot yhteensä (ml. Investoinnit)']
kokonaismenot = kokonaismenot.melt(id_vars="Toiminto", var_name="Vuosi",value_name="Miljoonaa euroa")
palvelutME = palvelutME.melt(id_vars="Toiminto", var_name="Vuosi",value_name="Miljoonaa euroa")
palvelujen_osuus = pd.merge(palvelutME, kokonaismenot, on="Vuosi", how="left")
palvelujen_osuus = palvelujen_osuus.rename(columns={"Miljoonaa euroa_x" : "Ikääntyneiden palvelut (miljoonaa euroa)",
                                                    "Miljoonaa euroa_y" : "Terveydenhuoltomenot yhteensä (miljoonaa euroa)",
                                                    "Toiminto_x" : "Toiminto"})
palvelujen_osuus["Osuus kokonaiskäyttömenoista (%)"] = (palvelujen_osuus["Ikääntyneiden palvelut (miljoonaa euroa)"] /
                                                                    palvelujen_osuus["Terveydenhuoltomenot yhteensä (miljoonaa euroa)"] * 100).round(2)
bar(palvelujen_osuus, "Osuus kokonaiskäyttömenoista (%)", "Toiminto", "Toiminto", "Ikääntyneiden palveluiden osuus terveydenhuollon kokonaiskäyttömenoista 2000-2022", "Vuosi" )


lineplt(kokonaismenot, "Vuosi", "Miljoonaa euroa", None, "Terveydenhuoltomenot vuosittain 2000-2022")

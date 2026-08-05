import json
import glob

titles = {
    "art_00": "Teknik i vardagen",
    "art_01": "Min granne soffpotatisen",
    "art_02": "Trött på att vara trött",
    "art_03": "Vad hände igår?",
    "art_04": "En stor förändring",
    "art_05": "Arbetsliv och karriär",
    "art_06": "Söka jobb för första gången",
    "art_07": "En spännande vecka på kontoret",
    "art_08": "En ny utbildning",
    "art_09": "Skola och examen",
    "art_10": "Repetera inför provet",
    "art_11": "En spännande folkhögskola",
    "art_12": "Kärleken till mat",
    "art_13": "Sockerberoende",
    "art_14": "Fika och mat",
    "art_15": "Konservera mat förr i tiden",
    "art_16": "Ett besök i mars",
    "art_17": "Ett litet brev",
    "art_18": "Cykla mountainbike",
    "art_19": "Ett möte i skogen",
    "art_20": "Miljöcertifierad park",
    "art_21": "En orörd del av Norden",
    "art_22": "Viktuppgång",
    "art_23": "Min nya avdelning",
    "art_24": "Hälsovård förr och nu",
    "art_25": "Den lilla byn på kullen",
    "art_26": "En typisk hurtbulle",
    "art_27": "Drömmen om god hälsa",
    "art_28": "Städning mitt i natten",
    "art_29": "Den gamla lägenheten",
    "art_30": "Min vardag",
    "art_31": "En stressig vecka",
    "art_32": "Sällskapsdamen från förr",
    "art_33": "Påskhelgen",
    "art_34": "Stugan vid bondgården",
    "art_35": "Kulturattraktion i norr",
    "art_36": "Konsthistoria",
    "art_37": "Dags för musikfestival",
    "art_38": "En skröna på internet",
    "art_39": "Litteratur och tankar",
    "art_40": "Mode och arkitektur",
    "art_41": "Livet som målare",
    "art_42": "En parlamentarisk demokrati",
    "art_43": "Statsskick och kungafamilj",
    "art_44": "Politiskt aktiv",
    "art_45": "Ett chockrosa kök",
    "art_46": "Läsa en ny bok",
    "art_47": "Ett möte på torget",
    "art_48": "Svensk politik och historia",
    "art_49": "Prata om relationer",
    "art_50": "Hej Maria!",
    "art_51": "Ett enormt arrangemang",
    "art_52": "En hemlig dröm",
    "art_53": "Hur är läget?",
    "art_54": "Kära Anna",
    "art_55": "Ett nytt liv med en vän",
    "art_56": "Mannen på vår lilla ö"
}

def main():
    files = glob.glob("articles/art_*.json")
    for f in files:
        with open(f, "r", encoding="utf-8") as file:
            data = json.load(file)
            
        art_id = data.get("article_id")
        if art_id in titles:
            data["article_title"] = titles[art_id]
            
            with open(f, "w", encoding="utf-8") as out:
                json.dump(data, out, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()

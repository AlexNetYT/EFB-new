from metar import Metar
import json, requests
from bs4 import BeautifulSoup
global vat_spy_data
vat_spy_data = {}
def get_runways(icao):
    # try:
        url = f'https://vatrus.info/airport/{icao}'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        quotes  = soup.find("table", class_='text-center table table-sm table-striped table-responsive-lg')
        items = quotes.find_all("th")
        output = {}
        for item in items:
            string = str(item)
            if "row" in string:
                runway = item.text.replace("R", "").replace("L", "").replace("C", "")
                hdg = int(str(runway.split("/")[0]).replace("0", "").replace("R", "").replace("L", "").replace("C", ""))*10
                print(hdg)
                output.update({runway: {"hdg": f"{hdg}", "url" : f'https://metar-taf.com/images/rwy/day-{str(runway.split("/")[0]).replace("0", "").replace("R", "").replace("L", "").replace("C", "")}.svg'}})
        return output
    # except Exception as e:
    #     return {"status": 500, "error": e}
def decode_metar(icao):
    global vat_spy_data
    icao=icao.upper()
    try:
        #get metar 
        response = requests.request("GET", f"http://metartaf.ru/{icao}.json")
        if response.status_code == 200:
            metar_dct = response.json()
            metar_str = metar_dct['metar'][20:]
            metar_report = Metar.Metar(metar_str)
            sky_cond = metar_report.sky_conditions('|')
            sky = sky_cond.split('|') if len(metar_report.sky_conditions('|').split('|')) > 1 else sky_cond
            weather_data = {
            'metar-text': metar_str,
            'wind-deg': round(metar_report.wind_dir._degrees),
            '🗼Airport': metar_dct['name'],
            '🕒Time of Observation': f"{metar_report.time.strftime('%H%M')}Z",
            '💨Wind': f"{round(metar_report.wind_dir._degrees)}° {metar_report.wind_speed.string().replace(' mps', 'MPS')} {''.join(['Gusts: ', str(metar_report.wind_gust)]) if metar_report.wind_gust != None else ''}",
            '👁️Visibility': metar_report.visibility("M"),
            
            '🛰️Weather Phenomena': metar_report.present_weather(),
            '🌡️Temperature': f"{round(metar_report.temp.value())}° {metar_report.temp._units}",
            '🌫️Dew Point': f"{round(metar_report.dewpt.value())}° {metar_report.dewpt._units}",
            '⏱️Altimeter':f"{round( metar_report.press.value())} {str(metar_report.press._units).replace('MB','hPa')}",
            
        }
            if isinstance(sky, list):
                for item in sky:
                    type, alt = item.split(" at ")
                    weather_data.update({"☁️"+type.capitalize(): alt})
            else: weather_data.update({"☁️Clouds": "No INFO"})

            weather_data.update({'Remarks': f"{metar_report.remarks()}"}) if metar_report.remarks() != "" else None
            weather_data.update({'🛫Runway Visual Range': metar_report.runway_visual_range("M")}) if metar_report.runway_visual_range("M") != "" else None
            return weather_data
        else:
            return {"⚠️Error": "404 Error", "ℹ️Hint":"Reenter code and try again"} 
    # except Metar.ParserError as e:
    #     return {"⚠️Error": "Station in This airport not found", "ℹ️ Hint":"Reenter code and try again"}
    #     # return f"Error parsing METAR: {e}"
    except Exception as err:
        return {"⚠️Error": "Something went wrong", "ℹ️ Hint":"Reenter code and try again", "📄": err}
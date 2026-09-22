import pandas as pd
import plotly.graph_objects as go
import gradio as gr
import schedule
import time
import requests



def fetch_dataset():
    url = #Enter the CSV file URL
    dataset = pd.read_csv(url)
    return dataset

def showRoutes(routes:list):
    if "All Routes" in routes:
        filtered_df = df
    else:
        filtered_df = df[(df['ROUTE_NO'].isin(routes))]
        #print(filtered_df)

    fig = go.Figure(go.Scattermapbox(
    lat=filtered_df['LATITUDE'].tolist(),
    lon=filtered_df['LONGITUDE'].tolist(),
    mode='markers',
    marker=go.scattermapbox.Marker(
        size=6
    ),
    hoverinfo="text",
    hovertemplate='<b>ROUTE_NO</b>: %{text}<br><b>Stop_Name</b>: %{customdata}',
    text=filtered_df['ROUTE_NO'].tolist(), 
    customdata=filtered_df['STOP_NAME'].tolist()
    ))
 
    fig.update_layout(
        mapbox_style="open-street-map",
        hovermode='closest',
        mapbox=dict(
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=12.99468,
                lon=80.25892
            ),
            pitch=0,
            zoom=9
        ),

        
    )
    filtered_df2 = filtered_df[["ROUTE_NO","STOP_NAME","TIMING"]]
    return fig,filtered_df2



def showStops(stops):
    fig = go.Figure(go.Scattermapbox(
    lat=[i[2] for i in stops],
    lon=[i[3] for i in stops],
    mode='markers',
    marker=go.scattermapbox.Marker(
        size=6
    ),
    hoverinfo="text",
    hovertemplate='<b>ROUTE_NO</b>: %{text}<br><b>Stop_Name</b>: %{customdata}',
    text=[i[0] for i in stops], 
    customdata=[i[1] for i in stops]
    ))
 
    fig.update_layout(
        mapbox_style="open-street-map",
        hovermode='closest',
        mapbox=dict(
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=12.99468,
                lon=80.25892
            ),
            pitch=0,
            zoom=9
        ),

        
    )

    return fig

df =fetch_dataset()
# Function to update dataset every 12 hours
def update_dataset():
    global df
    df = fetch_dataset()

# Schedule dataset update every 12 hours
schedule.every(12).hours.do(update_dataset)

# Function to continuously run scheduled tasks
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)
    


def geocode(address:str):
    url = #url + "/findGeoCoordinates"
    params = {
        "address":address
    }
    
    try:
        response = requests.get(url, json=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")
        return None
    

def calculate_distance(latitude: float, longitude: float, distance: float):
    url =  #url +"/calculateDistance"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "distance": distance
    }

    try:
        response = requests.get(url, json=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")
        return None


def nearestStops(address,dist):
    geocoordinates = dict(geocode(address))
    lat = geocoordinates["latitude"]
    lon = geocoordinates["longitude"]
    stops = dict(calculate_distance(lat,lon,dist))
    
    stops.pop('status',None)
    stops2d = [[v['Route_no'], v['Stop_name'], v['Latitude'], v['Longitude'], v['Timing']] for k, v in stops.items()]
    map=showStops(stops2d)
    return map,stops2d


def startGradio():
    Routes=["All Routes"]
    routes = df["ROUTE_NO"].unique().tolist()
    Routes.extend(routes)
    # Create the Gradio interface
    with gr.Blocks() as demo:
        text1 = gr.Text(value="College Bus Route Tracker",interactive=False,show_label=False)
        with gr.Tab("Route Map"):
            with gr.Column():
                
                routes = gr.CheckboxGroup(choices=Routes,label="Routes",value=["All Routes"])

                map_component = gr.Plot(min_width=600)
                table = gr.DataFrame(min_width=600)
                #btn = gr.Button(value="Update Filter")
                text2 = gr.Textbox(value="A app based on the research done by \n1.Sarath Rajan Senthilkumar \n2.Veer Jabak \n3.Gautham Vidyashankar \n4.Divij D\n5.Dr Srisakthi Saravanan",show_label=False,interactive=False)
                
            #demo.load(fn=showRoutes,inputs=[routes],outputs=[map_component,table])
            demo.load(fn=showRoutes,inputs=[routes],outputs=[map_component,table])
            routes.change(fn=showRoutes,inputs=[routes],outputs=[map_component,table])
            #btn.click(fn=showRoutes,inputs=[routes],outputs=[map_component,table])
        
        with gr.Tab("Nearest Stop Finder"):
            with gr.Column():
                text3 = gr.Text(show_label=False,placeholder="Enter your address")
                slider1 = gr.Slider(minimum=1,maximum=4,label="Select range")
                btn1 = gr.Button()
                map_component1 = gr.Plot(min_width=600)
                table1 = gr.DataFrame(min_width=600,headers=["Route_no","Stop_name","Latitude","Longitude","Timing"])
            btn1.click(fn=nearestStops,inputs=[text3,slider1],outputs=[map_component1,table1])

            demo.load()
        

    demo.launch()

if __name__ == "__main__":
    startGradio()
    run_scheduler()



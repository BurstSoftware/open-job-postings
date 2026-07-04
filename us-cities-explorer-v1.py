import streamlit as st
import pandas as pd
import io

# 1. Page Configuration
st.set_page_config(
    page_title="US Cities Explorer", 
    page_icon="🌆", 
    layout="wide"
)

# 2. Dataset Setup
# We embed your CSV data directly so the app runs standalone
CSV_DATA = """state,city1,city2,city3,city4,city5,city6,city7,city8,city9,city10
Alabama,Huntsville,Birmingham,Montgomery,Mobile,Tuscaloosa,Hoover,Auburn,Dothan,Madison,Decatur
Alaska,Anchorage,Fairbanks,Juneau,Wasilla,Sitka,Ketchikan,Knik-Fairview,Badger,North Pole,College
Arizona,Phoenix,Tucson,Mesa,Chandler,Gilbert,Glendale,Scottsdale,Tempe,Peoria,Surprise
Arkansas,Little Rock,Fayetteville,Fort Smith,Springdale,Jonesboro,Rogers,Conway,North Little Rock,Bentonville,Pine Bluff
California,Los Angeles,San Diego,San Jose,San Francisco,Fresno,Sacramento,Long Beach,Oakland,Bakersfield,Anaheim
Colorado,Denver,Colorado Springs,Aurora,Fort Collins,Lakewood,Thornton,Arvada,Westminster,Pueblo,Greeley
Connecticut,Bridgeport,Stamford,New Haven,Hartford,Waterbury,Norwalk,Danbury,New Britain,Meriden,Bristol
Delaware,Wilmington,Dover,Newark,Middletown,Smyrna,Milford,Seaford,Georgetown,Lewes,Clayton
Florida,Jacksonville,Miami,Tampa,Orlando,St. Petersburg,Cape Coral,Hialeah,Tallahassee,Fort Lauderdale,Pembroke Pines
Georgia,Atlanta,Columbus,Augusta,Macon,Savannah,South Fulton,Roswell,Warner Robins,Johns Creek,Alpharetta
Hawaii,Honolulu,East Honolulu,Pearl City,Hilo,Waipahu,Kailua,Mililani Town,Kaneohe,Kahului,Kihei
Idaho,Boise,Meridian,Nampa,Caldwell,Idaho Falls,Pocatello,Twin Falls,Rexburg,Post Falls,Moscow
Illinois,Chicago,Aurora,Joliet,Naperville,Rockford,Springfield,Peoria,Elgin,Waukegan,Champaign
Indiana,Indianapolis,Fort Wayne,Evansville,South Bend,Carmel,Fishers,Bloomington,Hammond,Lafayette,Jeffersonville
Iowa,Des Moines,Cedar Rapids,Davenport,Sioux City,Iowa City,Waterloo,Dubuque,Ames,West Des Moines,Council Bluffs
Kansas,Wichita,Overland Park,Kansas City,Olathe,Topeka,Lawrence,Shawnee,Lenexa,Salina,Hutchinson
Kentucky,Louisville,Lexington,Bowling Green,Owensboro,Covington,Richmond,Georgetown,Florence,Hopkinsville,Elizabethtown
Louisiana,New Orleans,Baton Rouge,Shreveport,Lafayette,Lake Charles,Kenner,Bossier City,Monroe,Alexandria,Houma
Maine,Portland,Lewiston,Bangor,South Portland,Auburn,Biddeford,Sanford,Brunswick,Scarborough,Saco
Maryland,Baltimore,Frederick,Gaithersburg,Rockville,Bowie,Annapolis,Hagerstown,Salisbury,College Park,Laurel
Massachusetts,Boston,Worcester,Springfield,Cambridge,Lowell,Brockton,Lynn,Quincy,Newton,Fall River
Michigan,Detroit,Grand Rapids,Warren,Sterling Heights,Ann Arbor,Lansing,Kalamazoo,Dearborn,Livonia,Flint
Minnesota,Minneapolis,Saint Paul,Rochester,Duluth,Bloomington,Brooklyn Park,Plymouth,Woodbury,Maple Grove,Eagan
Mississippi,Jackson,Gulfport,Southaven,Hattiesburg,Biloxi, Meridian,Tupelo,Olive Branch,Greenville,Madison
Missouri,Kansas City,Saint Louis,Springfield,Columbia,Independence,Lee's Summit,O'Fallon,St. Joseph,St. Charles,St. Peters
Montana,Billings,Missoula,Great Falls,Bozeman,Butte-Silver Bow,Helena,Kalispell,Belgrade,Whitefish,Anaconda
Nebraska,Omaha,Lincoln,Bellevue,Grand Island,Kearney,Fremont,Hastings,Norfolk,Scottsbluff,Columbus
Nevada,Las Vegas,Henderson,North Las Vegas,Reno,Sparks,Enterprise,Carson City,Sunrise Manor,Summerlin South,Paradise
New Hampshire,Manchester,Nashua,Concord,Dover,Rochester,Salem,Keene,Portsmouth,Laconia,Somersworth
New Jersey,Newark,Jersey City,Paterson,Lakewood,Elizabeth,Edison,Woodbridge,Toms River,Clifton,Trenton
New Mexico,Albuquerque,Las Cruces,Rio Rancho,Santa Fe,Roswell,Farmington,Clovis,Hobbs,Alamogordo,Carlsbad
New York,New York,Buffalo,Yonkers,Rochester,Syracuse,Albany,New Rochelle,Cheektowaga,Mount Vernon,Schenectady
North Carolina,Charlotte,Raleigh,Greensboro,Durham,Winston-Salem,Fayetteville,Cary,Wilmington,High Point,Burlington
North Dakota,Fargo,Bismarck,Grand Forks,Minot,West Fargo,Williston,Dickinson,Jamestown,Wahpeton,Devils Lake
Ohio,Columbus,Cleveland,Cincinnati,Toledo,Akron,Dayton,Parma,Canton,Lorain,Hamilton
Oklahoma,Oklahoma City,Tulsa,Norman,Broken Arrow,Edmond,Lawton,Moore,Stillwater,Midwest City,Enid
Oregon,Portland,Eugene,Salem,Gresham,Hillsboro,Bend,Beaverton,Medford,Springfield,Corvallis
Pennsylvania,Philadelphia,Pittsburgh,Allentown,Reading,Erie,Scranton,Bethlehem,Lancaster,Harrisburg,Altoona
Rhode Island,Providence,Warwick,Cranston,Pawtucket,East Providence,Woonsocket,Newport,Central Falls,Bristol,Westerly
South Carolina,Charleston,Columbia,North Charleston,Mount Pleasant,Rock Hill,Greenville,Summerville,Goose Creek,Florence,Myrtle Beach
South Dakota,Sioux Falls,Rapid City,Aberdeen,Brookings,Watertown,Mitchell,Yankton,Huron,Pierre,Brandon
Tennessee,Nashville,Memphis,Knoxville,Chattanooga,Clarksville,Murfreesboro,Franklin,Jackson,Johnson City,Bartlett
Texas,Houston,San Antonio,Dallas,Austin,Fort Worth,El Paso,Arlington,Corpus Christi,Plano,Laredo
Utah,Salt Lake City,West Valley City,West Jordan,Provo,Orem,Sandy,Draper,St. George,Taylorsville,Ogden
Vermont,Burlington,South Burlington,Rutland,Essex Junction,Barre,Montpelier,Winooski,St. Albans,Newport,Vergennes
Virginia,Virginia Beach,Chesapeake,Norfolk,Richmond,Newport News,Alexandria,Hampton,Roanoke,Portsmouth,Suffolk
Washington,Seattle,Spokane,Tacoma,Vancouver,Bellevue,Kent,Everett,Renton,Yakima,Federal Way
West Virginia,Charleston,Huntington,Morgantown,Parkersburg,Wheeling,Martinsburg,Weirton,Fairmont,Beckley,Clarksburg
Wisconsin,Milwaukee,Madison,Green Bay,Kenosha,Racine,Appleton,Waukesha,Eau Claire,Oshkosh,Janesville
Wyoming,Cheyenne,Casper,Gillette,Laramie,Rock Springs,Sheridan,Green River,Evanston,Riverton,Cody"""

# 3. Cache the data loading so it's snappy
@st.cache_data
def load_data():
    df = pd.read_csv(io.StringIO(CSV_DATA))
    return df

df = load_data()

# 4. Sidebar / Navigation
st.sidebar.title("Navigation 🧭")
app_mode = st.sidebar.radio("Choose a view:", ["Explore by State", "Search for a City"])

st.sidebar.markdown("---")
st.sidebar.info("This app visualizes the top 10 cities for all 50 US states.")

# 5. Main App Logic
st.title("🌆 The US Cities Explorer")

if app_mode == "Explore by State":
    st.markdown("### Browse the Top 10 Cities in Any State")
    
    # State selection dropdown
    selected_state = st.selectbox("Select a State:", df['state'].unique())
    
    # Filter data for the chosen state
    state_data = df[df['state'] == selected_state].iloc[0]
    
    st.divider()
    st.subheader(f"Top Cities in {selected_state} ✨")
    
    # Create a nice 5-column grid for the 10 cities
    cols1 = st.columns(5)
    cols2 = st.columns(5)
    
    # Populate the first row (Cities 1-5)
    for i in range(1, 6):
        with cols1[i-1]:
            st.metric(label=f"Rank #{i}", value=state_data[f"city{i}"])
            
    # Populate the second row (Cities 6-10)
    for i in range(6, 11):
        with cols2[i-6]:
            st.metric(label=f"Rank #{i}", value=state_data[f"city{i}"])

elif app_mode == "Search for a City":
    st.markdown("### Find Which State a City Belongs To")
    
    # Search bar
    search_query = st.text_input("Enter a city name (e.g., 'Springfield'):")
    
    if search_query:
        # Melt the dataframe from wide to long format for easy searching
        melted_df = df.melt(id_vars=["state"], var_name="rank", value_name="city")
        # Clean up the 'rank' column text (e.g., 'city1' -> '1')
        melted_df['rank'] = melted_df['rank'].str.replace('city', '#')
        
        # Filter for matches (case-insensitive)
        results = melted_df[melted_df['city'].str.contains(search_query, case=False, na=False)]
        
        if not results.empty:
            st.success(f"Found {len(results)} match(es) for '{search_query}'!")
            
            # Format the output table nicely
            display_df = results[['city', 'state', 'rank']].rename(
                columns={"city": "City", "state": "State", "rank": "Rank in State"}
            ).reset_index(drop=True)
            
            st.dataframe(display_df, use_container_width=True)
        else:
            st.warning("No cities found matching that name. Try another one!")

import pandas as pd
from latlong_math_dist import distance
from datetime import datetime, timedelta

# Get start time in GMT-3 timezone
start_gmt_minus_3_time = datetime.utcnow() + timedelta(hours=-3)
start_formatted_time = start_gmt_minus_3_time.strftime("%Y-%m-%d %H:%M:%S")
print(f"Current GMT-3 start time: {start_formatted_time}")

df = pd.DataFrame()
df['cep_origem'] = ['80040352']
df['cep_destino'] = ['05424000']

distancias = []
for iloc, row in df.iterrows():
    distancias.append(distance(row['cep_origem'], row['cep_destino']))

df['distancia_km'] = distancias

print(df)

# Get end time in GMT-3 timezone
end_gmt_minus_3_time = datetime.utcnow() + timedelta(hours=-3)
end_formatted_time = end_gmt_minus_3_time.strftime("%Y-%m-%d %H:%M:%S")
print(f"Current GMT-3 end time: {end_formatted_time}")
exec_time = (end_gmt_minus_3_time - start_gmt_minus_3_time)
print(f"Total execution time: {exec_time}")

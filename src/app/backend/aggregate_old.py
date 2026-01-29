from deltalake import DeltaTable, write_deltalake
import pandas as pd
from datetime import datetime, timedelta

def aggregate_old_data():
    dt = DeltaTable('delta/telemetry_raw')
    df = dt.to_pandas()
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    cutoff = datetime.utcnow() - timedelta(days=30)
    old = df[df['timestamp'] < cutoff]
    if old.empty:
        print('There are no data older than 30 days')
        return

    old['date'] = old['timestamp'].dt.date

    daily = (
        old
        .groupby(['date', 'sensor_id', 'device_id'])
        .agg(
            avg_value=('value', 'mean'),
            min_value=('value', 'min'),
            max_value=('value', 'max'),
            count=('value', 'count')
        )
        .reset_index()
    )

    write_deltalake(
        'delta/telemetry_daily',
        daily,
        mode='append',
        partition_by=['date']
    )

    dt.delete(f'timestamp < "{cutoff.isoformat()}"')

if __name__ == '__main__':
    aggregate_old_data()
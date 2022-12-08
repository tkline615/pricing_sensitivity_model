import pandas
import pandas as pd
import hvplot.pandas
import holoviews as hv

# Results of the survey nested within a dictionary

prices = {'Too Cheap': [100,120,200,200,300,100,100,300,100,350,340,450,100,257,109,109,280,400,250,200],
          'Cheap': [150,200,250,300,340,190,200,350,120,360,360,460,110,388,299,129,350,410,260,240],
          'Expensive': [400,400,450,350,400,200,300,370,180,370,490,490,130,433,399,149,400,420,270,280],
          'Too Expensive': [500,480,500,400,490,300,500,380,200,380,500,500,140,499,422,199,410,430,280,300],
        }

# Function will calculate the cumulative %s for each cohort
# In addition to plotting the 4 lines and suggesting the optimal price and acceptable range

def price_sensitivity_meter(df, interpolate=False):
    # convert data from wide to long
    # calculate frequency of each price for each group
    df1 = (df[['Too Cheap', 'Cheap', 'Expensive', 'Too Expensive']]
           .unstack()
           .reset_index()
           .rename(columns={'level_0': 'label', 0: 'prices'})[['label', 'prices']]
           .groupby(['label', 'prices'])
           .size()
           .reset_index()
           .rename(columns={0: 'frequency'})
           )
    # calculate cumsum percentages
    df1['cumsum'] = df1.groupby(['label'])['frequency'].cumsum()
    df1['sum'] = df1.groupby(['label'])['frequency'].transform('sum')
    df1['percentage'] = 100 * df1['cumsum'] / df1['sum']
    # convert data from long back to wide
    df2 = df1.pivot_table('percentage', 'prices', 'label')

    # take linear values in missing values
    if interpolate:
        df3 = df2.interpolate().fillna(0)
        df3['Too Cheap'] = 100 - df3['Too Cheap']
        df3['Cheap'] = 100 - df3['Cheap']
        plot = df3.hvplot(x='prices',
                          y=['Too Cheap', 'Cheap', 'Expensive', 'Too Expensive'],
                          ylabel='Percentage',
                          height=400,
                          color=['green', 'lightgreen', 'lightpink', 'crimson']
                          ).opts(legend_position='bottom')

    # forward fill
    else:
        df3 = df2.ffill().fillna(0)

        df3['Too Cheap'] = 100 - df3['Too Cheap']
        df3['Cheap'] = 100 - df3['Cheap']
        plot = df3.hvplot.step(x='prices',
                               y=['Too Cheap', 'Cheap', 'Expensive', 'Too Expensive'],
                               where='post',
                               ylabel='Percentage',
                               height=400,
                               color=['green', 'lightgreen', 'lightpink', 'crimson']
                               ).opts(legend_position='bottom')
    df3['optimal_diff'] = (df3['Too Cheap'] - df3['Too Expensive'])
    df3['left_diff'] = (df3['Too Cheap'] - df3['Expensive'])
    df3['right_diff'] = (df3['Too Expensive'] - df3['Cheap'])
    optimal = df3[df3['optimal_diff'] <= 0].index[0]
    lower_bound = df3[df3['left_diff'] <= 0].index[0]
    upper_bound = df3[df3['right_diff'] >= 0].index[0]

    optimal_line = hv.VLine(optimal).opts(color='blue', line_dash='dashed', line_width=0.4)

    lower_line = hv.VLine(lower_bound).opts(color='grey', line_dash='dashed', line_width=0.4)
    upper_line = hv.VLine(upper_bound).opts(color='grey', line_dash='dashed', line_width=0.4)

    print(f'Optimal Price: ${optimal}')
    print(f'Acceptable Price Range: ${lower_bound} to ${upper_bound}')

    return plot * lower_line * optimal_line * upper_line

if __name__ == '__main__':
    # data frame is organize the data
    df = pd.DataFrame(prices)
    df1 = price_sensitivity_meter(df)
    print(df1)
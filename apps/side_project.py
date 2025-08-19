import marimo

__generated_with = "0.14.16"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    import altair as alt
    return (alt,)


@app.cell
def _():
    import datetime
    return (datetime,)


@app.cell
def _():
    import pandas as pd
    import requests

    df = pd.read_csv("https://ourworldindata.org/grapher/prevalence-of-undernourishment.csv?v=1&csvType=full&useColumnShortNames=true", storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'})
    df.rename(columns={df.columns[-1]: "undernourishment"}, inplace=True)
    df = df.drop(columns=['Code'])

    return df, pd


@app.cell
def _(df):
    df
    return


@app.cell
def _(mo):
    options = ["World","Northern Africa (FAO)","South-eastern Asia (FAO)","South America (FAO)","Central Asia (FAO)","Sub-Saharan Africa (FAO)"]
    multiselect = mo.ui.multiselect(options=options,value=["Northern Africa (FAO)","South-eastern Asia (FAO)","South America (FAO)","Central Asia (FAO)","Sub-Saharan Africa (FAO)"])
    return (multiselect,)


@app.cell
def _(mo, multiselect):
    mo.hstack([multiselect, mo.md(f"Has value: {multiselect.value}")])
    return


@app.cell
def _(datetime, mo):
    start_date = datetime.date(2001,1,1).year
    end_date = datetime.date(2023,1,1).year
    date_range_slider = mo.ui.range_slider(
        start= start_date,
        stop = end_date,
        value=(start_date,end_date),
        label= "Select Year"
    )
    return (date_range_slider,)


@app.cell
def _(date_range_slider, mo):
    mo.hstack([date_range_slider])
    return


@app.cell
def _(date_range_slider):
    min = date_range_slider.value[0]
    max = date_range_slider.value[1]
    min
    max
    return max, min


@app.cell
def _(df, max, min, multiselect):
    df1 =df[df['Entity'].isin(multiselect.value) & (df['Year']>= min) & (df['Year'] <= max)]
    df1
    return (df1,)


@app.cell
def _(df):
    # Create a mapping of year to world undernourishment prevalence
    world_data = df[df['Entity'] == 'World'][['Year','undernourishment']]
    world_data.rename(columns={world_data.columns[-1]: "global_value"}, inplace=True)
    world_data
    return (world_data,)


@app.cell
def _(df1, world_data):
    df2 = df1.merge(world_data,left_on ='Year',right_on ='Year')
    df2['variance_to_world'] = df2['undernourishment'] - df2['global_value']
    df2
    return (df2,)


@app.cell
def _(df2):
    df2.columns
    return


@app.cell
def _(alt, df2, mo):
    chart = alt.Chart(df2).mark_line(point=alt.OverlayMarkDef(size=20),strokeWidth=2).encode(
    x=alt.X('Year:Q', axis=alt.Axis(format='d', title='Year')), 
    y=alt.Y('undernourishment:Q', axis=alt.Axis(title='Undernourishment Prevalence (%)')),
        color='Entity',
        tooltip=[
            'Entity', 
            'Year', 
            alt.Tooltip('undernourishment', title='Nourishment:', format='.1f', formatType='number')

        ]
    ).properties(title='Prevalence of Undernourishment Over Time by Region',font="Lato").configure_legend(orient="bottom",title=None).interactive()

    mo.ui.altair_chart(chart)
    return


@app.cell
def _(df2):
    df2
    return


@app.cell
def _(alt, df2, mo):
    color_scale = alt.condition(
            alt.datum.variance_to_world < 0,
            alt.value("steelblue"),  # When below 0
            alt.value("indianred")  # Otherwise
        )

    chart2 = alt.Chart(df2[df2['Entity'] != 'World']).mark_bar(size=2).encode(
                x=alt.X('Year:Q', axis=alt.Axis(format='d', title=None)),
                y=alt.Y('variance_to_world:Q', axis=alt.Axis(title='Variance to World')),
                color=color_scale,  
                column=alt.Column('Entity:N',title=None),  
                tooltip=[
                    'Entity', 
                    'Year', 
                    alt.Tooltip('undernourishment', title='undernourishment:', format='.1f', formatType='number'),
                    alt.Tooltip('variance_to_world', title='variance:', format='.1f', formatType='number')
                ]
            ).properties(
                title='Variance to World Undernourishment by Region (%)',
                font="Lato",
                width=100  # Adjust width as needed
            ).configure_legend(orient="bottom", title=None).interactive()

    mo.ui.altair_chart(chart2)
    return (color_scale,)


@app.cell
def _(alt, color_scale, df2, mo):

    chart3 = alt.Chart(df2[df2['Entity'] != 'World']).mark_bar(size=5).encode(
                    x=alt.X('Year:Q', axis=alt.Axis(format='d', title=None)),
                    y=alt.Y('variance_to_world:Q', axis=alt.Axis(title='Variance to World')),
                    color=color_scale,  
                    column=alt.Column('Entity:N', title=None, spacing=2),  # Added spacing parameter
                    tooltip=[
                        'Entity', 
                        'Year', 
                        alt.Tooltip('undernourishment', title='undernourishment:', format='.1f', formatType='number'),
                        alt.Tooltip('variance_to_world', title='variance:', format='.1f', formatType='number')
                    ]
                ).properties(
                    title='Variance to World Undernourishment by Region (%)',
                    font="Lato",
                    # Width set to "container" for responsive sizing
                    width="container"
                ).configure_legend(orient="bottom", title=None).configure_view(
                    continuousWidth=200  # Controls the default width behavior for the view
                ).interactive()

    mo.ui.altair_chart(chart3)
    return


@app.cell
def _():
    from vega_datasets import data

    source = data.barley()
    return (source,)


@app.cell
def _(source):
    source
    return


@app.cell
def _(alt, df2):
    alt.Chart(df2).mark_bar().encode(
        x='sum(variance_to_world):Q',
        y='Year:O',
    #    color='Year:N',
        row='Entity:N'
    )
    return


@app.cell
def _(alt, source):

    alt.Chart(source).mark_line().encode(
        x='year:O',
        y='median(yield)',
        color='site'
    )
    return


@app.cell
def _(df2, max, min):
    df3 = df2[(df2['Year']== min) & (df2['Year'] == max)]
    df3
    return


@app.cell
def _(df2):
    df2
    return


@app.cell
def _(df2, max, min, pd):
    most_recent = df2[df2['Year'] == max]
    earliest = df2[df2['Year'] == min]
    result = pd.concat([earliest,most_recent])
    return (result,)


@app.cell
def _(alt, result):
    alt.Chart(result).mark_line().encode(
        x='Year:O',
        y='variance_to_world',
        color='Entity'
    ).interactive()
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()

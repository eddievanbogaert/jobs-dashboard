-- Seed data for the series_metadata table.
MERGE `jobs-dashboard.labor_market.series_metadata` AS target
USING (
    SELECT * FROM UNNEST([
        STRUCT('PAYEMS'        AS series_id, 'Total Nonfarm Payrolls'          AS display_name, 'All employees, total nonfarm, seasonally adjusted'                       AS description, 'BLS/CES' AS source, 'monthly' AS frequency, 'Thousands of Persons' AS units, 'employment'   AS category),
        STRUCT('UNRATE',                     'Unemployment Rate',                               'Civilian unemployment rate, seasonally adjusted',                                    'BLS/CPS',            'monthly',             'Percent',                          'unemployment'),
        STRUCT('CIVPART',                    'Labor Force Participation Rate',                   'Civilian labor force participation rate, seasonally adjusted',                        'BLS/CPS',            'monthly',             'Percent',                          'employment'),
        STRUCT('CES0500000003',              'Average Hourly Earnings',                          'Average hourly earnings of all employees, total private, seasonally adjusted',        'BLS/CES',            'monthly',             'Dollars per Hour',                 'wages'),
        STRUCT('JTSJOL',                     'Job Openings (JOLTS)',                             'Job openings, total nonfarm, seasonally adjusted',                                   'BLS/JOLTS',          'monthly',             'Thousands',                        'job_openings'),
        STRUCT('ICSA',                       'Initial Jobless Claims',                           'Initial claims for unemployment insurance, seasonally adjusted',                     'DOL/ETA',            'weekly',              'Number',                           'claims'),
        STRUCT('U6RATE',                     'U-6 Underemployment Rate',                         'Total unemployed + marginally attached + part-time for economic reasons',             'BLS/CPS',            'monthly',             'Percent',                          'unemployment'),
        STRUCT('EMRATIO',                    'Employment-Population Ratio',                      'Civilian employment-population ratio, seasonally adjusted',                          'BLS/CPS',            'monthly',             'Percent',                          'employment')
    ])
) AS source
ON target.series_id = source.series_id
WHEN MATCHED THEN
    UPDATE SET
        display_name = source.display_name,
        description  = source.description,
        source       = source.source,
        frequency    = source.frequency,
        units        = source.units,
        category     = source.category
WHEN NOT MATCHED THEN
    INSERT (series_id, display_name, description, source, frequency, units, category)
    VALUES (source.series_id, source.display_name, source.description, source.source,
            source.frequency, source.units, source.category);

import math

import numpy_financial as npf
from TM1py import TM1Service

from constants import prod_params


def calculate_irr():
    with TM1Service(**prod_params) as tm1:
        # read investment cashflows from TM1
        mdx = """
        SELECT 
        NON EMPTY {Tm1SubsetAll([Investment Period])} ON ROWS,
        NON EMPTY {TM1SubsetAll([Investment])} ON COLUMNS
        FROM [Investments]
        WHERE ([Year].[2023], [InvestmentsMeasure].[Cashflow])
        """
        df = tm1.cells.execute_mdx_dataframe_shaped(mdx, use_blob=True)

        # loop through result set and consume it
        cells = dict()
        for investment in df.columns[1:]:
            cashflows = df[investment].astype(float).values

            irr = npf.irr(cashflows)

            cells["2023", "0", investment, "IRR"] = 0 if math.isnan(irr) else irr
        tm1.cells.write(cube_name="Investments", cellset_as_dict=cells, use_blob=True)

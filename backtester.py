from datetime import date,datetime, timedelta
import nsepy as ns

def get_option_data(startDate,endDate,optionType,strike,expiry):
    nifty_opt = ns.get_history(symbol="NIFTY",
                        start=startDate,
                        end=endDate,
                        index=True,
                        option_type=optionType,
                        strike_price=strike,
                        expiry_date=expiry)
    return nifty_opt
def get_nifty_data(startDate,endDate):
    nifty = ns.get_history(symbol="NIFTY",start=startDate,end=endDate,index=True)
    return nifty

def get_thursdays(start_date, end_date):
    thursdays = []
    current_date = start_date

    # Iterate over each date within the range
    while current_date <= end_date:
        if current_date.weekday() == 3:  # Thursday has index 3
            thursdays.append(current_date)

        current_date += timedelta(days=1)  # Increment the current date by one day

    return thursdays

def get_PL_ironc(date,spread,margin):
    nifty = get_nifty_data(date,date)
    if (nifty.empty):
        print("{} | Holiday".format(date))
        PL_percent = 0
        return PL_percent
    else:
        entry_spot = nifty.Open.iloc[0] #finding the entry strike price 
        entry_spot = round(entry_spot/50)*50
        nifty_opt_CE = get_option_data(date,date,"CE",entry_spot+spread,date)
        nifty_opt_CE_hedge = get_option_data(date,date,"CE",entry_spot+spread+100,date)
        nifty_opt_PE = get_option_data(date,date,"PE",entry_spot-spread,date)
        nifty_opt_PE_hedge = get_option_data(date,date,"PE",entry_spot-spread-100,date)
        if(nifty_opt_CE.empty or nifty_opt_PE.empty or nifty_opt_CE_hedge.empty or nifty_opt_PE_hedge.empty):
            print("{} | Data Unavailable".format(date))
            return 0
        CE_entry = nifty_opt_CE.Open.iloc[0]
        CE_exit = nifty_opt_CE.Last.iloc[0]
        CE_hedge_entry = nifty_opt_CE_hedge.Open.iloc[0]
        CE_hedge_exit = nifty_opt_CE_hedge.Close.iloc[0]
        PE_entry = nifty_opt_PE.Open.iloc[0]
        PE_exit = nifty_opt_PE.Last.iloc[0]
        PE_hedge_entry = nifty_opt_PE_hedge.Open.iloc[0]
        PE_hedge_exit = nifty_opt_PE_hedge.Close.iloc[0]
        PL_percent = ((PE_entry-PE_exit)+(CE_entry-CE_exit)+(CE_hedge_exit-CE_hedge_entry)+(PE_hedge_exit-PE_hedge_entry))*50*100/margin
        print("{} | {} CE | Entry = {} | Exit = {} ||| {} PE | Entry = {} | Exit = {} | P&L = {}".format(date,entry_spot+spread,CE_entry,CE_exit,entry_spot-spread,PE_entry,PE_exit,PL_percent.round(2)))
        return PL_percent
        
def implement(startDate,endDate,spread,margin):
    thursdays = get_thursdays(startDate,endDate)
    net_PL = 0
    print("------------Thursday Iron Condor Backtester----------")
    print("Lot Size = 50 || Approx Margin = {}".format(margin))
    no_trades = 0
    for i in thursdays:
        PL = get_PL_ironc(i,spread,margin)
        net_PL = net_PL + PL 
        
    print("************BACKTEST RESULTS**************")
    print("Net Profit & Loss = {}".format(net_PL))

implement(date(2022,1,1),date(2023,1,1),200,40000)






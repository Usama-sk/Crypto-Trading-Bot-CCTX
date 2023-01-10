#Phemex Trading Bot updated (30-01-2021)
#Shariq Account/Usman Khokhar's Code!!
import threading
from configparser import ConfigParser
from time import sleep
from datetime import datetime, date
from datetime import time
import time
import ccxt

# app = Flask(__name__)
# config_object = ConfigParser()
# config_object.read("Phemex_keys.ini")
# logininfo = config_object["LOGIN"]
# api = logininfo["api"]
# secret = logininfo["secret"]

exchange = ccxt.phemex({'apiKey': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxx', 'secret': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', 'enableRateLimit': True,
})


exchange.set_sandbox_mode(True)
# orders_at_the_time = 20
symbol = 'BTC/USD'
temp = ''
################
# current_total_balance = exchange.fetch_balance({'currency': 'BTC'})['BTC']['total']
# bitcoin_ticker = exchange.fetch_ticker(symbol=symbol)
# mark_price = (float(bitcoin_ticker['ask']) + float(bitcoin_ticker['bid'])) / 2
# one_order_value = 1 * (1 / mark_price)
# quantity_all_order = current_total_balance / one_order_value
# quantity_per_order = quantity_all_order / orders_at_the_time
# quantity_per_order = int(quantity_per_order)
# if(quantity_per_order > 650):
# quantity_per_order = 650
# else:
#     quantity_per_order = quantity_per_order
#############
quantity_per_order = 10000
print("**************************\nQuantity per Order : ", quantity_per_order, "\n**************************")
#Quantity End
def run():
    print('CCXT version:', ccxt.__version__)
    #pnl = 0
    starting_balance = exchange.fetch_balance({'currency': 'BTC'})['BTC']['total']
    print("\n*****************************************")
    print("Starting Balance\t:\t", starting_balance)
    print("*****************************************")

    clear_positions()
    sleep(5)
    cancel_sell_orders()
    sleep(5)

    while True:
        out = open('Phemex-Exception' + str(date.today()) + '.txt', 'a')
        exception = 0
        try:
            balance = exchange.fetch_balance()['free']['BTC']
            if (float(starting_balance) < float(balance)):
                out.write('[' + str(datetime.now()) + ']' + ' Balance  :  ' + str(balance) + " Increase\n")
            elif (float(starting_balance) > float(balance)):
                out.write('[' + str(datetime.now()) + ']' + ' Balance  :  ' + str(balance) + " Decrease\n")
            else:
                out.write('[' + str(datetime.now()) + ']' + ' Balance  :  ' + str(balance) + " Same\n")
            starting_balance = balance

            bitcoin_ticker = exchange.fetch_ticker(symbol=symbol)
            mark_price = (float(bitcoin_ticker['ask']) + float(bitcoin_ticker['bid'])) / 2

            positions = exchange.privateGetAccountsAccountpositions({"currency": "BTC"})['data']['positions'][0]
            liquidation_price = positions['liquidationPrice']
            difference = float(mark_price) - float(liquidation_price)
            qty = positions['size']
            if (int(qty) < 0):
                out.write('[' + str(datetime.now()) + ']' + "Positions Quantity going towards negative\nExit Trading Bot\n\n")
                print("Positions are going towards Negative or Closed short\nExit the Trading Bot")
                exit()

            check_Liquidation()
            sleep(5)

            if (difference > 15000):
                print("Liquidation Difference is Greater than 15000\nMore space for trade")
            else:
                print('\n----------------------------------\nToo many sell orders pending')
                print('Waiting for 5 minute(s) before placing next order...\n----------------------------------\n')
                time.sleep(5 * 60)
                continue

            bitcoin_ticker = exchange.fetch_ticker(symbol=symbol)
            starting_value = (float(bitcoin_ticker['ask']) + float(bitcoin_ticker['bid'])) / 2
            print("\nCurrent Market Price of Phemex\t:\t", starting_value)
            sleep(5)

            i = 1
            increase_counter = 0
            decrease_counter = 0

            while (i <= 10):
                now = datetime.now()
                dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                bitcoin_ticker = exchange.fetch_ticker(symbol=symbol)
                mark_price = (float(bitcoin_ticker['ask']) + float(bitcoin_ticker['bid'])) / 2
                print("\n-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-\n")

                if (mark_price < starting_value):
                    print("Iteration #\t:\t", i, "\nDate and Time\t:\t", dt_string, "\nBitcoin value decreases\n","current Value\t:\t", mark_price, "  $", "\nPrevious Value\t:\t", starting_value, " $")
                    temp = starting_value
                    starting_value = mark_price
                    decrease_counter = decrease_counter + 1

                elif (mark_price > starting_value):
                    print("Iteration #\t:\t", i, "\nDate and Time\t:\t", dt_string, "\nBitcoin value Increases\n","current Value\t:\t", mark_price, " $", "\nPrevious Value\t:\t", starting_value, " $")
                    temp = starting_value
                    starting_value = mark_price
                    increase_counter = increase_counter + 1
                else:
                    print("Iteration #\t:\t", i, "\nDate and Time\t:\t", dt_string,"\nBitcoin Value Neither Increase Nor Decrease")
                i = i + 1
                sleep(4)

            if (increase_counter > decrease_counter):
                print("\nContinue Increasing, so buy at +2 from the current value that is", float(mark_price) + 2, "\n")
                buy_value = float(mark_price) + 2
                sell_value = float(mark_price) + 50

            elif (decrease_counter > increase_counter):
                print("\nContinue Decreasing, so buy at -5 from the current value that is", float(mark_price) - 5, "\n")
                buy_value = float(mark_price) - 5
                sell_value = float(mark_price) + 50

            else:
                print("\nIncrease and Decrease ratio same, so again check it")
                continue

            now1 = datetime.now()
            dt_string = now1.strftime("%d/%m/%Y %H:%M:%S")
            print("Buy Order place of", quantity_per_order, "Quantities @", buy_value, "at", dt_string)
            orderID1 = exchange.create_limit_buy_order(symbol, quantity_per_order, buy_value)['info']['orderID']
            out.write('[' + str(datetime.now()) + '] '+ str(quantity_per_order) + ' Quantities Buy Order Place @ ' + str(buy_value) + '\n')
            sleep(5)

            buy_status = True
            while (buy_status == True):
                order_status = exchange.fetch_order_status(symbol=symbol , id = orderID1)
                if (order_status == 'closed'):
                    print("\n\t\t** Buy order closed **")
                    now3 = datetime.now()
                    dt_string3 = now3.strftime("%d/%m/%Y %H:%M:%S")
                    print("Buy Order Filled at\t:\t", dt_string3)
                    k = place_sell_order(sell_value)
                    out.write('[' + str(datetime.now()) + '] ' + str(quantity_per_order) + ' Quantites Sell Order Place @ ' + str(k) + '\n\n')
                    ########################################################
                    # pnl = pnl + (((quantity_per_order  1) / buy_value) - ((quantity_per_order  1) / k))
                    # print("\nRealized Pnl : ", pnl, "\n")
                    ########################################################
                    sell_counter = 0
                    open_order = exchange.fetch_open_orders(symbol=symbol)
                    for t in open_order:
                        side = t['info']['side']
                        if(side == 'Sell'):
                            sell_counter = sell_counter + 1
                    print("\nWaiting Time For Pair Trade is :", (sell_counter  ,10,  60) / 60, "Minutes")
                    sleep(sell_counter,  10,  60)
                    buy_status = False
                    break

                now2 = datetime.now()
                time_difference = now2 - now1
                time_difference = time_difference.seconds

                if (time_difference >= 10 * 60):
                    print("\n----------------------------------\nTime Up for Buy Order\nGoing to Cancel it")
                    p = 0
                    opened1 = exchange.fetch_open_orders(symbol=symbol)
                    for x in opened1:
                        open_orders3 = opened1[p]
                        side3 = open_orders3['info']['side']
                        remaining = open_orders3['remaining']
                        filled = open_orders3['filled']

                        if (side3 == 'Buy'):
                            print("found buy in active CANCEL")
                            if (remaining == quantity_per_order):
                                out.write('[' + str(datetime.now()) + '] Order Cancel || ' + str(remaining) + '\n\n')
                                order_id3 = open_orders3['info']['orderID']
                                exchange.cancel_order(id=order_id3, symbol=symbol)
                                print("Order has been cancel at ", now2, "\n----------------------------------")
                                buy_status = False
                                break
                            if (filled < quantity_per_order and filled > 0):
                                order_id3 = open_orders3['info']['orderID']
                                exchange.cancel_order(id=order_id3, symbol=symbol)
                                print("Order has been cancel at ", now2, "\n----------------------------------")
                                entry_price = exchange.privateGetAccountsAccountpositions({"currency": "BTC"})['data']['positions'][0]['avgEntryPrice']
                                exchange.create_limit_sell_order(symbol, filled, float(entry_price) + 50)
                                print("--------------------------------\nSell Order Place of", filled,"quantities @", float(entry_price) + 50," at\t:\t", now2,"\n----------------------------------")
                                out.write('[' + str(datetime.now()) + '] Order Cancel || Partial Filled || ' + str(filled) + '\n')
                                out.write('[' + str(datetime.now()) + '] ' + str(filled) + ' Quantites Sell Order Place @ ' + str(k) + '\n\n')
                                # j = float(entry_price) + 50
                                ########################################################
                                # pnl = pnl + (((filled  1) / buy_value) - ((filled  1) / j))
                                # print("\nRealized Pnl : ", pnl , "\n")
                                ########################################################
                                sell_counter = 0
                                open_order = exchange.fetch_open_orders(symbol=symbol)
                                for t in open_order:
                                    side = t['info']['side']
                                    if (side == 'Sell'):
                                        sell_counter = sell_counter + 1
                                print("\nWaiting Time For Pair Trade is :", (sell_counter  ,10,  60) / 60, "Minutes")
                                sleep(sell_counter,  10,  60)
                                buy_status = False
                            break
                        p = p + 1
                else:
                    print("\n** WAITING FOR BUY ORDER TO BE FULFILLED **")
                    sleep(20)

                if (buy_status == False):
                    break

        except ccxt.ExchangeError as e:
            print('Exchange error raised. Details below:\n', e)
            out.write('[' + str(datetime.now()) + '] ' + 'Exchange error raised\n[' + str(datetime.now()) + '] ' + str(e) + '\n\n')
            exception = 1
        except ccxt.NetworkError as e:
            print('Network error raised. Details below:\n', e)
            out.write('[' + str(datetime.now()) + '] ' + 'Network error raised\n[' + str(datetime.now()) + '] ' + str(e) + '\n\n')
            exception = 1
        except Exception as e:
            print('Exception raised. Details below:\n', e)
            out.write('[' + str(datetime.now()) + '] ' + str(e) + '\n\n')
            exception = 1

        if (exception == 1):
            print('Exception has been raised. Waiting for 10 minutes before placing next order...\n')
            time.sleep(10 * 60)
        out.close()

def place_sell_order(sell_value):
    out = open('Phemex-Exception' + str(date.today()) + '.txt', 'a')
    exception = 0
    try:
        print("\n----------------------------------\nPlace Sell Order")
        now4 = datetime.now()
        dt_string4 = now4.strftime("%d/%m/%Y %H:%M:%S")
        positions = exchange.privateGetAccountsAccountpositions({"currency": "BTC"})['data']['positions'][0]
        entry_price = positions['avgEntryPrice']
        if (float(entry_price) > float(sell_value)):
            exchange.create_limit_sell_order(symbol, quantity_per_order, float(entry_price) + 50)
            print("Sell Order Place of", quantity_per_order, "Quantities @", float(entry_price) + 50,"at\t:\t", dt_string4 , "\n----------------------------------")
            k = float(entry_price) + 50
            return k
        else:
            exchange.create_limit_sell_order(symbol, quantity_per_order, sell_value)
            print("Sell Order Place of", quantity_per_order, "Quantities @", float(sell_value),"at\t:\t", dt_string4 , "\n----------------------------------")
            k = sell_value
            return k

    except ccxt.ExchangeError as e:
        print('Exchange error raised. Details below:\n', e)
        out.write('[' + str(datetime.now()) + '] ' + 'Exchange error raised\n['  + str(datetime.now()) + '] ' + str(e) + '\n\n')
        exception = 1
    except ccxt.NetworkError as e:
        print('Network error raised. Details below:\n' , e)
        out.write('[' + str(datetime.now()) + '] ' + 'Network error raised\n['  + str(datetime.now()) + '] ' + str(e) + '\n\n')
        exception = 1
    except Exception as e:
        print('Exception raised. Details below:\n' , e)
        out.write('[' + str(datetime.now()) + '] ' + str(e) + '\n\n')
        exception = 1

    if (exception == 1):
        print('Exception has been raised. Waiting for 10 minutes before placing next order...\n')
        time.sleep(10 * 60)
    out.close()

def check_Liquidation():
    out = open('Phemex-Exception' + str(date.today()) + '.txt', 'a')
    exception = 0
    try:
        print("\n######################### Check Liquidation Starts #########################")
        openn = exchange.fetch_open_orders(symbol)
        p = 0
        if (openn != []):
            for y in openn:
                side = y['info']['side']
                if(side == 'Sell'):
                    orderID = y['info']['orderID']
                    break
                p = p + 1
        else:
            print("No Open Orders Found")

        bitcoin_ticker = exchange.fetch_ticker(symbol=symbol)
        mark_price = (float(bitcoin_ticker['ask']) + float(bitcoin_ticker['bid'])) / 2
        positions = exchange.privateGetAccountsAccountpositions({"currency": "BTC"})['data']['positions'][0]
        size = positions['size']
        liquidation_price = positions['liquidationPrice']
        entry_price = positions['avgEntryPrice']
        print("*****************************************\nSize Position\t\t\t:\t", size)
        print("Liquidation Price\t\t:\t", liquidation_price)
        print("Mark Price\t\t\t\t:\t", mark_price)
        if (int(size) > 0):
            difference = float(mark_price) - float(liquidation_price)
            print("Difference\t\t\t\t:\t", difference, "\n*****************************************")
            if (difference <= 15000):
                out.write('[' + str(datetime.now()) + '] ' + "Liquidation Difference going Less than 15000\n\n")
                order_remaining = exchange.fetchOrder(orderID, symbol)['remaining']
                exchange.cancel_order(id=orderID, symbol=symbol)
                print("One Order has been cancel\nDifference less than 15000\nPlacing sell order")
                # if (order_remaining <= quantity_per_order):
                #     order_remaining1 = order_remaining-45000
                #     print(order_remaining1,  "placed on market order")
                #     exchange.create_market_sell_order(symbol, order_remaining1)
                #     sleep(10)
                #     order_remaining = order_remaining-order_remaining1
                #       if order_remaining >= 5000:
                print(order_remaining, "placed on limit order at price", entry_price)
                exchange.create_limit_sell_order(symbol, order_remaining, entry_price)
                sleep(60)

            else:
                print("************* Difference is greater than 15000 *************")
        else:
            print("No Buy Position Found...!")
        print("######################### Check Liquidation Ends ###########################\n")

    except ccxt.ExchangeError as e:
        print('Exchange error raised. Details below:\n', e)
        out.write('[' + str(datetime.now()) + '] ' + 'Exchange error raised\n['  + str(datetime.now()) + '] ' + str(e) + '\n\n')
        exception = 1
    except ccxt.NetworkError as e:
        print('Network error raised. Details below:\n' , e)
        out.write('[' + str(datetime.now()) + '] ' + 'Network error raised\n['  + str(datetime.now()) + '] ' + str(e) + '\n\n')
        exception = 1
    except Exception as e:
        print('Exception raised. Details below:\n' , e)
        out.write('[' + str(datetime.now()) + '] ' + str(e) + '\n\n')
        exception = 1

    if (exception == 1):
        print('Exception has been raised. Waiting for 10 minutes before placing next order...\n')
        time.sleep(10 * 60)
    out.close()

def clear_positions():
    out = open('Phemex-Exception' + str(date.today()) + '.txt', 'a')
    exception = 0
    try:
        out.write('[' + str(datetime.now()) + '] ' + "Clear Positions happened\n")
        threading.Timer(21600.0, clear_positions).start()  # called every 6 hours
        print("\n######################### Clear Position Starts #########################")
        opened = exchange.fetch_open_orders(symbol)
        p = 0
        total_sell_quantity_in_open = 0
        for x in opened:
            open_orders = opened[p]
            side = open_orders['info']['side']
            if (side == "Sell"):
                qty = open_orders['info']['orderQty']
                total_sell_quantity_in_open = float(total_sell_quantity_in_open) + float(qty)
            p = p + 1

        positions = exchange.privateGetAccountsAccountpositions({"currency": "BTC"})['data']['positions'][0]
        size = positions['size']
        entry_price = positions['avgEntryPrice']
        difference = float(size) - float(total_sell_quantity_in_open)

        bitcoin_ticker = exchange.fetch_ticker(symbol=symbol)
        mark_price = (float(bitcoin_ticker['ask']) + float(bitcoin_ticker['bid'])) / 2

        print("*****************************************\nSize Position\t\t\t:\t", size)
        print("Quantity Open\t\t\t:\t", total_sell_quantity_in_open)
        print("Mark Price\t\t\t\t:\t", mark_price)
        print("Entry Price\t\t\t\t:\t", entry_price)
        print("Difference\t\t\t\t:\t", difference, "\n*****************************************")

        if (difference > 0):
            out.write('[' + str(datetime.now()) + '] ' + "Placing Sell order of " + str(difference) + " quantity\n\n")
            if (float(mark_price) > float(entry_price)):
                print("Placing Sell order of ", difference, " quantity")
                exchange.create_limit_sell_order(symbol, difference,  float(mark_price) + 25)
            else:
                print("Placing Sell order of ", difference, " quantity")
                exchange.create_limit_sell_order(symbol, difference,  float(entry_price) + 25)
        else:
            out.write('[' + str(datetime.now()) + '] ' + "No Difference Found between the Quantities of Positions and Open Orders\n\n")
            print("No Difference Found...!")
        print("######################### Clear Position Ends ###########################\n")

    except ccxt.ExchangeError as e:
        print('Exchange error raised. Details below:\n', e)
        out.write('[' + str(datetime.now()) + '] ' + 'Exchange error raised\n['  + str(datetime.now()) + '] ' + str(e) + '\n\n')
        exception = 1
    except ccxt.NetworkError as e:
        print('Network error raised. Details below:\n' , e)
        out.write('[' + str(datetime.now()) + '] ' + 'Network error raised\n['  + str(datetime.now()) + '] ' + str(e) + '\n\n')
        exception = 1
    except Exception as e:
        print('Exception raised. Details below:\n' , e)
        out.write('[' + str(datetime.now()) + '] ' + str(e) + '\n\n')
        exception = 1

    if (exception == 1):
        print('Exception has been raised. Waiting for 10 minutes before placing next order...\n')
        time.sleep(10 * 60)
    out.close()


def cancel_sell_orders():
    out = open('Phemex-Exception' + str(date.today()) + '.txt', 'a')
    exception = 0
    try:
        out.write('[' + str(datetime.now()) + '] ' + "Cancel Sell Order happened\n")
        threading.Timer(21600.0, cancel_sell_orders).start()  # called every 6 hours
        print("\n######################### Cancel Sell Orders Starts #########################")

        positions = exchange.privateGetAccountsAccountpositions({"currency": "BTC"})['data']['positions'][0]
        entry_price = positions['avgEntryPrice']
        buy_count = 0
        sell_count = 0
        remain = 0
        counter = 0
        open_orders = exchange.fetch_open_orders(symbol=symbol)
        for j in range(len(open_orders)):
            order_age = exchange.milliseconds() - open_orders[j]['timestamp']
            order_age_minutes = order_age / 1000 / 60
            print('Order time: ' + open_orders[j]['datetime'] + ' & age (approx in minutes): ' + str(round(order_age_minutes, 1)))
            if (open_orders[j]['side'] == 'buy'):
                buy_count = buy_count + 1
            if (open_orders[j]['side'] == 'sell'):
                sell_count = sell_count + 1
                if (order_age_minutes >= 24 * 60):
                    counter = counter + 1
                    print('\n*****This order is more than 24 hours old*****')
                    print('Canceling the old order')
                    order_remaining = exchange.fetchOrder(open_orders[j]['info']['orderID'], symbol=symbol)['remaining']
                    exchange.cancelOrder(open_orders[j]['info']['orderID'], symbol=symbol)
                    print('Selling on market price')
                    if (order_remaining <= quantity_per_order):
                        remain = remain + order_remaining
                        print("Place Market Sell Order")
                        exchange.create_limit_sell_order(symbol, order_remaining, float(entry_price) + 20)
        out.write('[' + str(datetime.now()) + ']' + " Cancel " + str(counter) + " Sell order(s) and ReOrder " + str(remain) + " quantity w.r.t current Market Price\n\n")
        print('Total Open Orders: ' + str(len(open_orders)) + ' [Buy: ' + str(buy_count) + ' *** Sell: ' + str(sell_count) + ']')
        print("######################### Cancel Sell Orders Ends ###########################\n")

    except ccxt.ExchangeError as e:
        print('Exchange error raised. Details below:\n', e)
        out.write('[' + str(datetime.now()) + '] ' + 'Exchange error raised\n['  + str(datetime.now()) + '] ' + str(e) + '\n\n')
        exception = 1
    except ccxt.NetworkError as e:
        print('Network error raised. Details below:\n' , e)
        out.write('[' + str(datetime.now()) + '] ' + 'Network error raised\n['  + str(datetime.now()) + '] ' + str(e) + '\n\n')
        exception = 1
    except Exception as e:
        print('Exception raised. Details below:\n' , e)
        out.write('[' + str(datetime.now()) + '] ' + str(e) + '\n\n')
        exception = 1

    if (exception == 1):
        print('Exception has been raised. Waiting for 10 minutes before placing next order...\n')
        time.sleep(10 * 60)
    out.close()

if __name__ == "__main__":
    run()
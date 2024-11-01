import yfinance as yf; from datetime import datetime as dt; import time
import os; import pygame as pg; import tkinterRunner

pg.init()
# Setting up the pygame window for the UI, technically just a viewing screen right now though.
#       Later you should set up a connection to Robinhood or various other trading platforms so that you can buy and sell with just a click.
class window:
    dimensions = (800, 400)
    screen = pg.display.set_mode(dimensions)
    clock = pg.time.Clock()

    # Setting the window name.
    pg.display.set_caption("Stock Analyzer")

    # Font Setup
    font = pg.font.Font(os.getcwd() + "/ocr.ttf", 25)
    text = font.render("Hello", True, "black")

    # Background and buy/sell text setup.
    bg = pg.Surface(dimensions); bg.fill("black")
    textDimensions = (72, 20)
    textBG = pg.Surface(textDimensions); textBG.fill("white")

def etfPriceRetrieval(ticker):
    flag = False

    startDate = dt.today().strftime('%Y-%m-%d')
    if dt.today().weekday() == 0:
        startDate = startDate[:-2] + str(int(startDate[-2:]) - 3)
    elif dt.today().weekday() == 6:
        startDate = startDate[:-2] + str(int(startDate[-2:]) - 2)
    else:
        startDate = startDate[:-2] + str(int(startDate[-2:]) - 1)

    stock = yf.download(ticker, start=startDate, end=dt.today().strftime('%Y-%m-%d'))
    price = stock["Close"]
    open(os.getcwd()+ "/data/temp.txt", "w").truncate(0)
    open(os.getcwd()+ "/data/temp.txt", "w").write(str(price))

    #price = str(price[price.index(str(startDate)) + 10:])

    # ***Some formatting kinks need to be worked out here, but the algorithm works.***

    lines = open(os.getcwd() + "/data/temp.txt", "r").readlines(); string2 = ""
    for x in lines:
        if "." in x: string2 = x

    p = string2[14:]
    p = str(round(float(p), 2))

    return p

# Taking information from the tkinter input window, parsing it, then writing it to our stockData.txt file.
def writeToFile():
    flag = False
    info = tkinterRunner.returnItems()
    ticker = info[0].upper()
    bs = "S" if info[2] == "Sold" else "B"

    # Checking if an inputted stock is a stock or an ETF by checking if finding the price normally works or not.
    # If it doesn't, we get a ValueError and use another way.

    try:
        price = float(info[1])
        stockInfo = ticker + ":" + bs + "," + str(price)

        f = open(os.getcwd() + "/data/stockData.txt", "r"); lines = f.readlines(); f.close()
        string = ""
        for x in lines:
            if ticker in x:
              string += stockInfo + "\n"
              flag = True
            else: string += x
        f = open(os.getcwd() + "/data/stockData.txt", "w");
        f.write(string + "\n") if flag else f.write(string + "\n" + stockInfo); f.close()

    except ValueError:
        p =  etfPriceRetrieval(ticker) + "\n"

        lines = open(os.getcwd() + "/data/etfData.txt", "r").readlines(); string = ""
        for x in lines:
            string += x

        stockInfo = (ticker + ":" + bs + "," + p).replace(" ", "")
        open(os.getcwd() + "/data/etfData.txt", "w").write(string + stockInfo)
        open(os.getcwd()+ "/data/temp.txt", "w").truncate(0)

# Setting up tkinter for the entry message boxes.
run = True
# Main loop
while run:
    # Pygame event loop to make the screen show up.
    for event in pg.event.get():
        if event.type == pg.quit:
            pg.quit(); exit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit(); exit()
            if event.key == pg.K_TAB:
                tkinterRunner.main()
                writeToFile()

    # Getting the information from the stockData.txt file and parsing it into 3 lists. Tickers, last bought/sold, prices at which bought/sold.
    f = open(os.getcwd() + "/data/stockData.txt", "r"); temp = f.readlines(); tickers = []; bs = []; prices = [];
    # Initializing variables for the while loop to use.
    previousPrice = 0; priceChange = 0; txtLST = []; color = ""

    # Parsing the information in the text file into the 3 lists.
    for x in temp:
        if x == "\n": continue
        x = x.split(":"); tickers.append(x[0])
        x = x[1].split(","); bs.append(x[0]); prices.append(float(x[1].replace("\n", "")))

    # Below is a delay function in case you don't want the code running every second.
    #time.sleep(5)
    # Loop to get the individual ticker information.
    for y in tickers:
        # Right now, we are just retrieving the ticker infor from yahoo finance as it updates.
        priceInfo = str(yf.Ticker(y).info).split(","); price = ""
        symbolInfo = str(yf.Ticker(y).info).split(","); symbol = ""

        # Parsing the ticker info from yahoo finance to get the price and symbol.
        # This loop could DEFINITELY be optimized, consider rewriting entirely.
        for x in priceInfo:
            if "currentPrice" in x:
                price = x
                price = str(round(float(price[price.index(":") + 2:]), 2))
                if len(price[price.index("."):]) < 3: price += "0"
                for x in symbolInfo:
                    if "symbol" in x:
                        symbol = x
                        symbol = symbol[symbol.index(":") + 2:]
                if len(price) < 6: price += (" " * (6 - len(price)))
                if len(symbol) < 6: symbol += (" " * (6 - len(symbol)))
                previousPrice = float(prices[tickers.index(y)]);
                priceChange = round(-((previousPrice - float(price)) / float(price)) * 100, 3)
                if priceChange > 0: priceChange = "+" + str(priceChange)
                # Printing the ticker info for each ticker in the tickers list to the terminal.
                print(symbol, " : ", price, dt.now().strftime("%d/%m/%Y %H:%M:%S"), priceChange)

        # Formatting specific tickers. Ignore this, to be optimized later but for now it is hard-coded for Lucid and AMD.
        if len(price) < 6: price += (" " * (6 - len(price)))
        if len(price[price.index("."):]) < 3: price += "0"
        if len(symbol.replace("'", "").replace(" ", "")) == 3: symbol += " "

        # This is the variable for how low and how high the buy/sell should be.
        PERCENTAGE_CHECKED = 7
        PRICE_CHANGE = 5
        print(float(price) * (float(priceChange) / 100))

        # Checking the text file to see if a stock was recently bought or sold, then using that to figure out if the stock should be sold
        # if the price goes above 7% or bought if it dips below -7%. If neither, the option is to keep the stock.
        if bs[tickers.index(symbol.replace("'", "").replace(" ", ""))] == "B" and float(priceChange) > PERCENTAGE_CHECKED or (float(price) * (float(priceChange) / 100)) > PRICE_CHANGE: val = "Sell"
        elif bs[tickers.index(symbol.replace("'", "").replace(" ", ""))] == "S" and float(priceChange) < -PERCENTAGE_CHECKED: val = "Buy"
        else: val = "Keep"

        # Formatting the ticker information to print to the screen.
        text = str(symbol + " : " + price)

        # Adding all the information to be printed to the screen to a list so they are all in one place to be referenced.
        txtLST.append([text, str(priceChange), val, price, yf.Ticker(y).info["fiftyTwoWeekHigh"], yf.Ticker(y).info["fiftyTwoWeekLow"]])

    # Rendering Work
    window.screen.blit(window.bg, (0, 0))

    window.text = window.font.render(dt.now().strftime("%m/%d/%Y %H:%M:%S"), True, "White")
    window.screen.blit(window.text, (260, 5)); vshift = 40

    # Rendering work.
    for n in txtLST:
        # Rendering the ticker information.
        window.text = window.font.render(n[0], True, "white")
        window.screen.blit(window.text, (2, txtLST.index(n) * 24 + vshift))

        # Rendering the price change percentage (priceChange).
        if float(n[1]) == 0: color = "yellow"
        elif "+" in n[1]: color = "green"
        else: color = "red"
        window.text = window.font.render(n[1], True, color)
        window.screen.blit(window.text, (222, txtLST.index(n) * 24 + vshift))

        # Rendering whether to buy, keep, or sell the stock.
        if n[2] == "Keep": color = "yellow"
        elif n[2] == "Sell": color = "green"
        else: color = "red"
        window.text = window.font.render(str(n[2]), True, "black")
        window.textBG.fill(color)
        window.screen.blit(window.textBG, (337, txtLST.index(n) * 24 + 5 + vshift))
        window.screen.blit(window.text, (342, txtLST.index(n) * 24 + vshift))

        # Rendering the weekly highest stock price.
        window.text = window.font.render("52 High: " + str(n[4]), True, "light green")
        window.screen.blit(window.text, (417, txtLST.index(n) * 24 + vshift))

        # Rendering the weekly low stock price.
        window.text = window.font.render("Low: " + str(n[5]), True, "#FF474C")
        window.screen.blit(window.text, (632, txtLST.index(n) * 24 + vshift))

    # Rendering ETFs.
    window.text = window.font.render("ETFs & Others", True, "white")
    vshift += len(txtLST) * 24 + 10 + vshift
    window.screen.blit(window.text, (300, vshift))
    vshift += 15

    etfLST = open(os.getcwd() + "/data/etfData.txt", "r").readlines()
    tempList = []; info = []
    for x in etfLST:
        tempList = x.split(":")
        tempList.append((tempList[1].split(","))[0])
        tempList.append(tempList[1][tempList[1].index(","):].replace(",", ""))
        tempList.pop(1)

        if len(str(tempList[0])) == 3:
            window.text = window.font.render("  \'" + tempList[0] + "\'   :", True, "white")
        else:
            window.text = window.font.render("\'" + tempList[0] + "\' :", True, "white")

        window.screen.blit(window.text, (2, vshift + 24 * (etfLST.index(x) + 1)))

        strPrice = tempList[2][:-1]
        if len(tempList[2][:-1]) < 6: strPrice += "0"
        strCurPrice = etfPriceRetrieval(tempList[0])
        if len(strCurPrice) < 6: strCurPrice += "0"
        perChange = round(((float(strCurPrice) - float(strPrice)) / float(strCurPrice)) * 100, 2)
        if perChange >= 0: perChange = "  " + str(perChange)
        perChange = str(perChange) + "%"

        # Remove perChange from the rendering work under this line, add it to another line and render it the proper % change color.
        window.text = window.font.render("Bought - " + strPrice + "     Last Close - " + strCurPrice + "     " + perChange, True, "white")
        window.screen.blit(window.text, (127, vshift + 24 * (etfLST.index(x) + 1)))

    pg.display.update()
    window.clock.tick(60)
    txtLST = []
    print()

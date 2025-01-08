select ticker, count(ticker) from sp500_stocks_price
group by ticker 


SELECT * FROM index_price

select * from sp500_stocks_price where ticker = 'TSCO'

truncate table sp500_stocks_price
delete 
from sp500_holdings
select * from sp500_stocks_price where stocksplits <>0
select * from sp500_holdings
select * from index_price
update index_price
set name = 'NASDAQ'
where ticker = '^IXIC'

select * from stocks_price 
update stocks_price
set IndexName = 'sp500'

select * from stocks_price where ticker='AAPL'
where indexName <>'sp500' and stocksplits <> 0
delete from stocks_price
where indexName <>'sp500'
insert into stocks_Price(Ticker,date, close,volume, stocksplits)
select Ticker,date, close,volume, stocksplits
from sp500_stocks_price
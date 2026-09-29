from fastapi import APIRouter
from ..services.ledger_rebuild import rebuild,list_entries
router=APIRouter()
@router.post("/ledger/rebuild/{period}")
def ledger_rebuild(period:str):return rebuild(period)
@router.get("/ledger/show/{show_id}")
def ledger_show(show_id:str,period:str|None=None):return list_entries(period=period,show_id=show_id)
@router.get("/ledger/book/{book_id}")
def ledger_book(book_id:str,period:str|None=None):return list_entries(period=period,book_id=book_id)
@router.get("/ledger/author/{author_id}")
def ledger_author(author_id:str,period:str|None=None):return list_entries(period=period,author_id=author_id)

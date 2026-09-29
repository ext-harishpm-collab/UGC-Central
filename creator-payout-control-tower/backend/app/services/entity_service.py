from ..db.session import SessionLocal
from ..models import Author, ContentItem, PaymentTransaction, BankAccount, Earning

def author_360(author_id, period=None):
    db=SessionLocal()
    try:
        a=db.query(Author).filter_by(author_id=author_id).first()
        banks=db.query(BankAccount).filter_by(author_id=author_id).all()
        earns=db.query(Earning).filter(Earning.author_id==author_id)
        pays=db.query(PaymentTransaction).filter(PaymentTransaction.author_id==author_id)
        if period:
            earns=earns.filter(Earning.payment_period==period)
            pays=pays.filter(PaymentTransaction.payment_period==period)
        return {
            "author":{"author_id":a.author_id,"name":a.name,"status":a.status} if a else None,
            "bank_accounts":[{"account_number":b.account_number,"ifsc":b.ifsc,"bank_name":b.bank_name,
                              "verification_status":b.verification_status,"successful_payment_count":b.successful_payment_count,
                              "current":b.is_current} for b in banks],
            "earnings":[{"period":e.payment_period,"book_id":e.book_id,"show_id":e.show_id,"type":e.reward_type,
                         "content_type":e.content_type,"gross":float(e.gross or 0),"net":float(e.net or 0),
                         "excluded":e.exclusion_reason} for e in earns.limit(5000).all()],
            "payments":[{"period":p.payment_period,"book_id":p.book_id,"show_id":p.show_id,"status":p.status,
                        "net":float(p.amount_after_tax or 0),"utr":p.utr,"ledger_state":p.ledger_state} for p in pays.limit(5000).all()]
        }
    finally:
        db.close()

def content_360(content_id, period=None):
    db=SessionLocal()
    try:
        q=db.query(ContentItem)
        if content_id:
            q=q.filter((ContentItem.book_id==content_id)|(ContentItem.show_id==content_id))
        c=q.first()
        if not c:return {"content":None,"earnings":[],"payments":[]}
        eq=db.query(Earning).filter((Earning.book_id==c.book_id)|(Earning.show_id==c.show_id))
        pq=db.query(PaymentTransaction).filter((PaymentTransaction.book_id==c.book_id)|(PaymentTransaction.show_id==c.show_id))
        if period:
            eq=eq.filter(Earning.payment_period==period);pq=pq.filter(PaymentTransaction.payment_period==period)
        return {
            "content":{"book_id":c.book_id,"show_id":c.show_id,"author_id":c.author_id,"content_type":c.content_type,
                       "parent_book_id":c.parent_book_id,"parent_show_id":c.parent_show_id,"relationship_type":c.relationship_type},
            "earnings":[{"period":e.payment_period,"reward_type":e.reward_type,"gross":float(e.gross or 0),"net":float(e.net or 0),"excluded":e.exclusion_reason} for e in eq.limit(5000).all()],
            "payments":[{"period":p.payment_period,"status":p.status,"net":float(p.amount_after_tax or 0),"utr":p.utr,"ledger_state":p.ledger_state} for p in pq.limit(5000).all()]
        }
    finally: db.close()

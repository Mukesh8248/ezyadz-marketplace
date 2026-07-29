from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def wallet_view(request):
    wallet = request.user.wallet

    transactions = wallet.transactions.select_related(
        "booking"
    ).all()

    return render(
        request,
        "wallets/wallet.html",
        {
            "wallet": wallet,
            "transactions": transactions,
        },
    )
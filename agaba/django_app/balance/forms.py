from django import forms

from .models import Replenishment, Withdrawal


class ReplenishmentForm(forms.ModelForm):
    """Форма для пополнения баланса"""

    class Meta:
        model = Replenishment
        fields = ['amount_replenishment']
        
    
class WithdrawalForm(forms.ModelForm):
    """Форма для вывода средств с баланса."""
    
    class Meta:
        model = Withdrawal
        fields = ['amount_withdrawal', 'inn']


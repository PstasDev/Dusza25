from django import forms
from .models import Kazamata, Vilagkartya, Vezerkartya


class KazamataForm(forms.ModelForm):
    """Form a kazamata létrehozásához és szerkesztéséhez"""
    
    class Meta:
        model = Kazamata
        fields = ['nev', 'tipus']
        widgets = {
            'nev': forms.TextInput(attrs={
                'class': 'input-field',
                'placeholder': 'pl. A sötét kripta',
                'maxlength': 100
            }),
            'tipus': forms.Select(attrs={
                'class': 'input-field'
            }),
        }
        labels = {
            'nev': 'Kazamata neve',
            'tipus': 'Kazamata típusa'
        }


class VilagkartyaForm(forms.ModelForm):
    """Form a világkártya létrehozásához és szerkesztéséhez"""
    
    class Meta:
        model = Vilagkartya
        fields = ['nev', 'tipus', 'sebzes', 'eletero']
        widgets = {
            'nev': forms.TextInput(attrs={
                'class': 'input-field',
                'placeholder': 'pl. Tűz varázsló',
                'maxlength': 16
            }),
            'tipus': forms.Select(attrs={
                'class': 'input-field'
            }),
            'sebzes': forms.NumberInput(attrs={
                'class': 'input-field',
                'min': 2,
                'max': 100,
                'placeholder': '2-100'
            }),
            'eletero': forms.NumberInput(attrs={
                'class': 'input-field',
                'min': 1,
                'max': 100,
                'placeholder': '1-100'
            }),
        }
        labels = {
            'nev': 'Kártya neve',
            'tipus': 'Elem típusa',
            'sebzes': 'Sebzés',
            'eletero': 'Életerő'
        }


class VezerkartyaForm(forms.ModelForm):
    """Form a vezérkártya létrehozásához"""
    
    class Meta:
        model = Vezerkartya
        fields = ['eredeti_kartya', 'duplazas_tipusa']
        widgets = {
            'eredeti_kartya': forms.Select(attrs={
                'class': 'input-field',
                'onchange': 'updatePreview()'
            }),
            'duplazas_tipusa': forms.RadioSelect()
        }
        labels = {
            'eredeti_kartya': 'Alap kártya',
            'duplazas_tipusa': 'Mit duplázunk?'
        }

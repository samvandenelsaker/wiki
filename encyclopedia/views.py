from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms

import secrets

from . import util

class SearchForm(forms.Form):
    your_name = forms.CharField(label='Search', max_length=100)

class CreatePageForm(forms.Form):
    title = forms.CharField(label='Title')
    content = forms.CharField(widget=forms.Textarea)

class UpdatePageForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea)

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": SearchForm()
    })

def entry(request, entry):
    entry_details = util.get_entry(entry)
    if entry_details != None:
        return render_entry_details(request, entry)
    else:
        raise Http404

def search(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            search_command = form.cleaned_data["your_name"].capitalize()
            entry_details = util.get_entry(search_command)
            if entry_details != None:
                return HttpResponseRedirect(reverse("encyclopedia:entry",
                    kwargs={'entry': search_command}))
                return render_entry_details(request, search_command)
            else:
                return render(request, "encyclopedia/search.html", {
                    "entries": util.search_query_entries(search_command),
                    "form": SearchForm()
                })

def create(request):
    if request.method == 'POST':
        form = CreatePageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if util.save_entry(title, content) == False:
                return render(request, "encyclopedia/create.html", {
                    "form": SearchForm(),
                    "createForm": CreatePageForm(),
                    "errorMessage" : "Page already exists!"
                    })

    return render(request, "encyclopedia/create.html", {
        "form": SearchForm(),
        "createForm": CreatePageForm()
    })

def random(request):
    pages = util.list_entries()
    random_entry = secrets.choice(pages)
    return HttpResponseRedirect(reverse("encyclopedia:entry",
        kwargs={'entry': random_entry}))

def update(request, entry):
    if request.method == 'POST':
        form = UpdatePageForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["content"]
            util.update_entry(entry, content)
            return HttpResponseRedirect(reverse("encyclopedia:entry",
                kwargs={'entry': entry}))

    entry_details = util.get_entry(entry)
    return render(request, "encyclopedia/update.html", {
        "form": SearchForm(),
        "entry": entry,
        "updatePageForm": UpdatePageForm({'content': entry_details})
    })

def render_entry_details(request, entry):
    return render(request, "encyclopedia/entry.html", {
        "entry": util.get_entry(entry),
        "title": entry.capitalize(),
        "form": SearchForm()
    })

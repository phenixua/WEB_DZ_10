from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views import View


from .forms import QuoteForm, AuthorForm, AuthorEditForm
from .models import Author, Quote, Tag


def main(request, page=1):
    # Отримуємо всі цитати разом з даними авторів та користувачів
    quotes = get_list_or_404(Quote.objects.select_related('author', 'user').all())

    elem_per_page = 10
    paginator = Paginator(quotes, elem_per_page)
    quotes_on_page = paginator.page(page)

    return render(request, "quotes/index.html", context={"quotes": quotes_on_page})


def author_detail(request, author_id):
    author = get_object_or_404(Author, id=author_id)
    return render(request, "quotes/author_detail.html", context={"author": author})


@login_required
def add_quote(request):
    if request.method == 'POST':
        quote_form = QuoteForm(request.POST)
        author_form = AuthorForm(request.POST)

        if quote_form.is_valid():
            # Отримуємо або створюємо автора
            author_name = request.POST.get('fullname')
            author, created = Author.objects.get_or_create(fullname=author_name, defaults={'user': request.user})

            # Зберігаємо цитату та пов'язуємо її з автором
            quote = quote_form.save(commit=False)
            quote.user = request.user
            quote.author = author
            quote.save()

            # Обробка тегів
            tags = quote_form.cleaned_data['tags']
            tag_objects = [Tag.objects.get_or_create(name=tag.strip())[0] for tag in tags]
            quote.tags.set(tag_objects)

            # Перенаправлення на сторінку зі списком цитат
            return redirect('quotes:root')
    else:
        quote_form = QuoteForm()
        author_form = AuthorForm()

    return render(request, 'quotes/add_quote.html', {'quote_form': quote_form, 'author_form': author_form})


@login_required
def edit_author(request, author_id):
    author = get_object_or_404(Author, id=author_id)

    # Перевіряємо, що поточний користувач створював автора
    if request.user.id != author.user.id:
        # Якщо не є, виконуємо перенаправлення
        return redirect('quotes:root')

    if request.method == 'POST':
        form = AuthorEditForm(request.POST, instance=author)
        if form.is_valid():
            # Зберігаємо зміни в даних автора
            form.save()
            return redirect('quotes:author_detail', author_id=author_id)
    else:
        form = AuthorEditForm(instance=author)

    return render(request, 'quotes/edit_author.html', {'form': form, 'author': author})


@login_required
def delete_quote(request, quote_id):
    quote = get_object_or_404(Quote, id=quote_id)

    if request.user.is_authenticated and quote.user == request.user:
        author = quote.author
        quote.delete()

        # Перевіряємо, чи є ще цитати автора
        if Quote.objects.filter(author=author).count() == 0:
            # Якщо більше немає цитат автора, видаляємо автора
            author.delete()

        return JsonResponse({'message': 'Your Quote was deleted successfully.'})
    else:
        return JsonResponse({'message': 'Your access was not authorized or Quote does not exist.'}, status=401)


class TagQuotesView(View):
    template_name = 'quotes/tag_quotes.html'
    quotes_per_page = 10

    def get(self, request, *args, **kwargs):
        # Тут ключ ['tag_name'] тому, що у файлi urls.py заданий шлях <str:tag_name>
        tag_name = kwargs['tag_name']
        tag = get_object_or_404(Tag, name=tag_name)
        quotes_with_tag = get_list_or_404(Quote.objects.filter(tags=tag))

        paginator = Paginator(quotes_with_tag, self.quotes_per_page)
        page = request.GET.get('page')

        try:
            quotes_per_page = paginator.page(page)
        except (PageNotAnInteger, EmptyPage):
            quotes_per_page = paginator.page(1)

        context = {
            'tag_name': tag_name,
            'quotes_with_tag': quotes_per_page,
        }

        return render(request, self.template_name, context)

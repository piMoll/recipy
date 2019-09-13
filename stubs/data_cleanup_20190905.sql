

UPDATE public.recipes_ingredient
    SET quantity = replace(quantity, 'Teelöffel', 'TL')
    WHERE quantity LIKE '%Teelöffel'
;

UPDATE public.recipes_ingredient
    SET quantity = replace(quantity, 'Esslöffel', 'EL')
    WHERE quantity LIKE '%Esslöffel'
;
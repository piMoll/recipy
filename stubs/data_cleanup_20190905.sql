
-- Attr quantity: Teelöffel -> TL
UPDATE public.recipes_ingredient
    SET quantity = replace(quantity, 'Teelöffel', 'TL')
    WHERE quantity LIKE '%Teelöffel'
;

-- Attr quantity: Esslöffel -> EL
UPDATE public.recipes_ingredient
    SET quantity = replace(quantity, 'Esslöffel', 'EL')
    WHERE quantity LIKE '%Esslöffel'
;

-- Attr name: Esslöffel -> EL + nach quantity verschieben
UPDATE public.recipes_ingredient
    SET
        quantity = regexp_replace(name, '.* Esslöffel .*', regexp_replace(name, ' Esslöffel .*', ' EL')),
        name = regexp_replace(name, '.* Esslöffel ', '')
    WHERE name LIKE '%Esslöffel%'
;

-- Attr name: Teelöffel -> TL
UPDATE public.recipes_ingredient
    SET
        name = regexp_replace(name, 'Teelöffel', 'TL')
    WHERE name LIKE '%Teelöffel%'
;

-- Attr quantity: Quantity-Info aus Attr name holen
UPDATE public.recipes_ingredient
    SET
        quantity = regexp_replace(name, 'TL .*', 'TL'),
        name = regexp_replace(name, '.* TL ', '')
    WHERE name LIKE '%TL%' AND quantity = ''
;

-- Attr name: 3 Leerschläge entfernen
UPDATE public.recipes_ingredient
    SET
        name = replace(name, '   ', ' ')
    WHERE name LIKE '%   %'
;

-- Attr name: 2 Leerschläge entfernen
UPDATE public.recipes_ingredient
    SET
        name = replace(name, '  ', ' ')
    WHERE name LIKE '%  %'
;

-- Attr quantity: Trailing whitespace
UPDATE public.recipes_ingredient
    SET
        quantity = trim(quantity)
    WHERE quantity LIKE '% '
;

-- Attr description: 3 Leerschläge entfernen
UPDATE public.recipes_direction
    SET
        description = replace(description, '   ', ' ')
    WHERE description LIKE '%   %'
;

-- Attr description: 2 Leerschläge entfernen
UPDATE public.recipes_direction
    SET
        description = replace(description, '  ', ' ')
    WHERE description LIKE '%  %'
;

#!/usr/bin/env python3
"""Traducción EN TIEMPO DE ARMADO de la central de reservas (reservasnueva/index.html y reservasnueva/_ficha.html).

Las plantillas siguen en ESPAÑOL (una sola fuente de verdad). `traducir(src, 'pt'|'en')` aplica PARES (es -> pt, en):
subcadenas EXACTAS de las plantillas. Se aplican en UNA sola pasada (regex con las alternativas ordenadas de más larga a
más corta): lo ya traducido nunca se vuelve a traducir y un par corto no pisa a uno largo que lo contiene.

REGLAS PARA AGREGAR O CAMBIAR TEXTO
  1. Texto nuevo en una plantilla -> su par acá en el MISMO cambio. Correr tools/probar-i18n-reservas.py: debe dar 0 restos.
  2. Cada par lleva el contexto que lo hace único (comillas del literal, > < de la etiqueta, espacio inicial...). No se traduce
     nunca un identificador, clave de objeto, valor de data-*, clase CSS, URL ni parámetro de query (llegada, salida, adultos...).
  3. En PT/EN NO usar apóstrofes ni comillas dobles dentro de la traducción (muchos pares viven dentro de literales JS '...'
     o atributos "..."): "you will", "I am", "does not".
  4. Las URLs estáticas del HTML que apuntan a /reservasnueva/ se cambian con pares (href="/reservasnueva/" -> .../pt/).
     En JS siempre se usa la constante BASE (meta php-base, que el armado cambia por idioma con el par de la meta).
  5. Selector de idioma: metas php-alt-es|pt|en. En index.html ya vienen completas (/reservasnueva/, /pt/, /en/). En _ficha.html
     son marcadores __ALT_ES__/__ALT_PT__/__ALT_EN__ que completa tools/generar-fichas.py con la ruta de ESA propiedad en cada
     idioma (si quedan sin completar, el JS las ignora y los links quedan como están).

Los documentos legales y el resumen de reglas salen de tools/legales_reserva.py (RESUMEN) y de las páginas del sitio por idioma.

Formato de _DATOS (abajo): bloques separados por línea en blanco; cada línea 'ES: texto¦', 'PT: texto¦', 'EN: texto¦' (el ¦ final
delimita el valor, así se conservan espacios en los bordes; '\\n' = salto de línea). Si falta PT o EN, se deja igual que el español.
"""
import os, re, sys

_DATOS = r'''

ES: 'Huéspedes'¦
PT: 'Hóspedes'¦
EN: 'Guests'¦

ES: 'Dormitorios'¦
PT: 'Quartos'¦
EN: 'Bedrooms'¦

ES: 'Baños'¦
PT: 'Banheiros'¦
EN: 'Bathrooms'¦

ES: 'Gimnasio'¦
PT: 'Academia'¦
EN: 'Gym'¦

ES: 'Aire acond.'¦
PT: 'Ar-cond.'¦
EN: 'A/C'¦

ES: 'Cochera'¦
PT: 'Garagem'¦
EN: 'Parking'¦
ES: <html lang="es">¦
PT: <html lang="pt-BR">¦
EN: <html lang="en">¦

ES: <title>Reservas en Punta del Este | Premium Host Punta</title>¦
PT: <title>Reservas em Punta del Este | Premium Host Punta</title>¦
EN: <title>Book in Punta del Este | Premium Host Punta</title>¦

ES: Casas y apartamentos premium en Punta del Este, La Barra, Manantiales y Montevideo. Reservá directo con Premium Host Punta: disponibilidad y precio real al instante.¦
PT: Casas e apartamentos premium em Punta del Este, La Barra, Manantiales e Montevidéu. Reserve direto com a Premium Host Punta: disponibilidade e preço real na hora.¦
EN: Premium houses and apartments in Punta del Este, La Barra, Manantiales and Montevideo. Book direct with Premium Host Punta: real availability and price instantly.¦

ES: | Reservas Premium Host Punta</title>¦
EN: | Premium Host Punta Bookings</title>¦

ES: <meta name="php-base" content="/reservasnueva/" />¦
PT: <meta name="php-base" content="__BASE_PT__" />¦
EN: <meta name="php-base" content="__BASE_EN__" />¦

ES: <span class="active">ES</span>\n      <span class="sep">·</span>\n      <a href="/pt/index.html" hreflang="pt">PT</a>\n      <span class="sep">·</span>\n      <a href="/en/index.html" hreflang="en">EN</a>¦
PT: <a href="__BASE_ES__" hreflang="es">ES</a>\n      <span class="sep">·</span>\n      <span class="active">PT</span>\n      <span class="sep">·</span>\n      <a href="__BASE_EN__" hreflang="en">EN</a>¦
EN: <a href="__BASE_ES__" hreflang="es">ES</a>\n      <span class="sep">·</span>\n      <a href="__BASE_PT__" hreflang="pt">PT</a>\n      <span class="sep">·</span>\n      <span class="active">EN</span>¦

ES: aria-label="LinkedIn de Felipe Zerbino"¦
EN: aria-label="Felipe Zerbino on LinkedIn"¦

ES: aria-label="Menú"¦
PT: aria-label="Menu"¦
EN: aria-label="Menu"¦

ES: <a href="/index.html" class="logo">¦
PT: <a href="/pt/index.html" class="logo">¦
EN: <a href="/en/index.html" class="logo">¦

ES: <a href="/index.html">Inicio</a>¦
PT: <a href="/pt/index.html">Início</a>¦
EN: <a href="/en/index.html">Home</a>¦

ES: <a href="/reservasnueva/" class="current">Reservas</a>¦
PT: <a href="__BASE_PT__" class="current">Reservar</a>¦
EN: <a href="__BASE_EN__" class="current">Book</a>¦

ES: <a href="/reservasnueva/">Reservas</a>¦
PT: <a href="__BASE_PT__">Reservar</a>¦
EN: <a href="__BASE_EN__">Book</a>¦

ES: <a href="/como-trabajamos.html">Cómo&nbsp;trabajamos</a>¦
PT: <a href="/pt/como-trabalhamos.html">Como&nbsp;trabalhamos</a>¦
EN: <a href="/en/how-we-work.html">How&nbsp;we&nbsp;work</a>¦

ES: <a href="/como-trabajamos.html">Cómo trabajamos</a>¦
PT: <a href="/pt/como-trabalhamos.html">Como trabalhamos</a>¦
EN: <a href="/en/how-we-work.html">How we work</a>¦

ES: <a href="/conocenos.html">Conócenos</a>¦
PT: <a href="/pt/sobre-nos.html">Sobre nós</a>¦
EN: <a href="/en/about-us.html">About us</a>¦

ES: <a href="/propietarios.html">Propietarios</a>¦
PT: <a href="/pt/proprietarios.html">Proprietários</a>¦
EN: <a href="/en/owners.html">Owners</a>¦

ES: <a href="/contacto.html">Contacto</a>¦
PT: <a href="/pt/contato.html">Contato</a>¦
EN: <a href="/en/contact.html">Contact</a>¦

ES: id="volver" href="/reservasnueva/"¦
PT: id="volver" href="__BASE_PT__"¦
EN: id="volver" href="__BASE_EN__"¦

ES: ‹ Todas las propiedades¦
PT: ‹ Todas as propriedades¦
EN: ‹ All properties¦

ES: <p>Gestión premium de alquileres vacacionales en Punta del Este, La Barra, Manantiales, Punta Ballena, Montevideo y Rocha.</p>¦
PT: <p>Gestão premium de aluguéis de temporada em Punta del Este, La Barra, Manantiales, Punta Ballena, Montevidéu e Rocha.</p>¦
EN: <p>Premium vacation rental management in Punta del Este, La Barra, Manantiales, Punta Ballena, Montevideo and Rocha.</p>¦

ES: <h4>Navegación</h4>¦
PT: <h4>Navegação</h4>¦
EN: <h4>Navigation</h4>¦

ES: <h4>Contacto</h4>¦
PT: <h4>Contato</h4>¦
EN: <h4>Contact</h4>¦

ES: <li>Punta del Este, Uruguay</li>¦
PT: <li>Punta del Este, Uruguai</li>¦

ES: <a href="/aviso-legal.html">Aviso legal</a>¦
PT: <a href="/pt/aviso-legal.html">Aviso legal</a>¦
EN: <a href="/en/legal-notice.html">Legal notice</a>¦

ES: <a href="/condiciones-generales.html">Condiciones generales</a>¦
PT: <a href="/pt/termos.html">Termos de uso</a>¦
EN: <a href="/en/terms.html">Terms of service</a>¦

ES: <a href="/politica-privacidad.html">Política de privacidad</a>¦
PT: <a href="/pt/politica-privacidade.html">Política de privacidade</a>¦
EN: <a href="/en/privacy-policy.html">Privacy policy</a>¦

ES: <a href="/politica-cookies.html">Política de cookies</a>¦
PT: <a href="/pt/politica-cookies.html">Política de cookies</a>¦
EN: <a href="/en/cookie-policy.html">Cookie policy</a>¦

ES: <span>RUT 220520320015</span>¦
PT: <span>CNPJ 220520320015</span>¦
EN: <span>Tax ID 220520320015</span>¦

ES: <span>Registro MINTUR N°2011</span>¦
EN: <span>MINTUR Registry N°2011</span>¦

ES: <div>Punta del Este · Uruguay¦
PT: <div>Punta del Este · Uruguai¦

ES: Acceso equipo¦
PT: Acesso da equipe¦
EN: Team access¦

ES: aria-label="Escribir por WhatsApp"¦
PT: aria-label="Escrever pelo WhatsApp"¦
EN: aria-label="Message us on WhatsApp"¦

ES: <span class="eyebrow">Reserva directa · Precio real al instante</span>¦
PT: <span class="eyebrow">Reserva direta · Preço real na hora</span>¦
EN: <span class="eyebrow">Book direct · Real price instantly</span>¦

ES: <h1>Tu lugar en <em>Punta del Este</em></h1>¦
PT: <h1>Seu lugar em <em>Punta del Este</em></h1>¦
EN: <h1>Your place in <em>Punta del Este</em></h1>¦

ES: Casas y apartamentos que gestionamos nosotros, con el estándar Premium Host Punta. Elegí fechas y ves disponibilidad y precio final, sin sorpresas.¦
PT: Casas e apartamentos que nós mesmos gerenciamos, com o padrão Premium Host Punta. Escolha as datas e veja a disponibilidade e o preço final, sem surpresas.¦
EN: Houses and apartments that we manage ourselves, to the Premium Host Punta standard. Pick your dates and see availability and the final price, no surprises.¦

ES: <span>Precio final con limpieza incluida</span>¦
PT: <span>Preço final com limpeza incluída</span>¦
EN: <span>Final price with cleaning included</span>¦

ES: <span>Equipo local en Punta del Este</span>¦
PT: <span>Equipe local em Punta del Este</span>¦
EN: <span>Local team in Punta del Este</span>¦

ES: <span>Atención por WhatsApp</span>¦
PT: <span>Atendimento por WhatsApp</span>¦
EN: <span>Support on WhatsApp</span>¦

ES: <span class="lbl">Llegada</span>¦
PT: <span class="lbl">Chegada</span>¦
EN: <span class="lbl">Check-in</span>¦

ES: <span class="lbl">Salida</span>¦
PT: <span class="lbl">Saída</span>¦
EN: <span class="lbl">Check-out</span>¦

ES: <span class="lbl">Huéspedes</span>¦
PT: <span class="lbl">Hóspedes</span>¦
EN: <span class="lbl">Guests</span>¦

ES: >Elegí una fecha<¦
PT: >Escolha uma data<¦
EN: >Pick a date<¦

ES: 'Elegí una fecha'¦
PT: 'Escolha uma data'¦
EN: 'Pick a date'¦

ES: >2 personas<¦
PT: >2 pessoas<¦
EN: >2 guests<¦

ES: <label for="selZona">Zona</label>¦
PT: <label for="selZona">Região</label>¦
EN: <label for="selZona">Area</label>¦

ES: Todas las zonas¦
PT: Todas as regiões¦
EN: All areas¦

ES: id="btnBuscar">Buscar</button>¦
PT: id="btnBuscar">Buscar</button>¦
EN: id="btnBuscar">Search</button>¦

ES: <b>Adultos</b><small>13 años o más</small>¦
PT: <b>Adultos</b><small>13 anos ou mais</small>¦
EN: <b>Adults</b><small>13 years or older</small>¦

ES: <b>Niños</b><small>De 2 a 12 años</small>¦
PT: <b>Crianças</b><small>De 2 a 12 anos</small>¦
EN: <b>Children</b><small>Ages 2 to 12</small>¦

ES: <b>Bebés</b><small>Menores de 2 (no cuentan)</small>¦
PT: <b>Bebês</b><small>Menores de 2 anos (não contam)</small>¦
EN: <b>Infants</b><small>Under 2 (not counted)</small>¦

ES: 'ad|Adultos|13 años o más'¦
PT: 'ad|Adultos|13 anos ou mais'¦
EN: 'ad|Adults|13 years or older'¦

ES: 'ni|Niños|De 2 a 12 años'¦
PT: 'ni|Crianças|De 2 a 12 anos'¦
EN: 'ni|Children|Ages 2 to 12'¦

ES: 'be|Bebés|Menores de 2 (no cuentan)'¦
PT: 'be|Bebês|Menores de 2 anos (não contam)'¦
EN: 'be|Infants|Under 2 (not counted)'¦

ES: >Filtros <b¦
EN: >Filters <b¦

ES: data-v="casa">Casas<¦
EN: data-v="casa">Houses<¦

ES: data-v="apartamento">Apartamentos<¦
EN: data-v="apartamento">Apartments<¦

ES: aria-label="Dormitorios"¦
PT: aria-label="Dormitórios"¦
EN: aria-label="Bedrooms"¦

ES: <option value="0">Dormitorios</option>¦
PT: <option value="0">Dormitórios</option>¦
EN: <option value="0">Bedrooms</option>¦

ES: + dormitorios</option>¦
PT: + dormitórios</option>¦
EN: + bedrooms</option>¦

ES: Reservás y pagás online, sin esperar aprobación¦
PT: Você reserva e paga online, sem esperar aprovação¦
EN: Book and pay online, no waiting for approval¦

ES: >⚡ Inmediata<¦
PT: >⚡ Imediata<¦
EN: >⚡ Instant<¦

ES: data-f="piscina">Piscina<¦
EN: data-f="piscina">Pool<¦

ES: data-f="frente_mar">Frente al mar<¦
PT: data-f="frente_mar">Frente para o mar<¦
EN: data-f="frente_mar">Oceanfront<¦

ES: data-f="playa">Cerca de la playa<¦
PT: data-f="playa">Perto da praia<¦
EN: data-f="playa">Near the beach<¦

ES: data-f="parrillero">Parrillero<¦
PT: data-f="parrillero">Churrasqueira<¦
EN: data-f="parrillero">BBQ grill<¦

ES: data-f="jacuzzi">Jacuzzi<¦
EN: data-f="jacuzzi">Hot tub<¦

ES: aria-label="Ordenar"¦
PT: aria-label="Ordenar"¦
EN: aria-label="Sort"¦

ES: >Recomendadas</option>¦
EN: >Recommended</option>¦

ES: >Precio: menor a mayor</option>¦
PT: >Preço: menor para maior</option>¦
EN: >Price: low to high</option>¦

ES: >Precio: mayor a menor</option>¦
PT: >Preço: maior para menor</option>¦
EN: >Price: high to low</option>¦

ES: >Más dormitorios</option>¦
PT: >Mais dormitórios</option>¦
EN: >Most bedrooms</option>¦

ES: id="btnEquipo">Armar selección</button>¦
PT: id="btnEquipo">Montar seleção</button>¦
EN: id="btnEquipo">Build a selection</button>¦

ES: Mostrando solo lo que está en la zona del mapa.¦
PT: Mostrando só o que está na região do mapa.¦
EN: Showing only what is inside the map area.¦

ES: id="zonaQuitar">Ver todas<¦
PT: id="zonaQuitar">Ver todas<¦
EN: id="zonaQuitar">Show all<¦

ES: >Mostrar más propiedades<¦
PT: >Mostrar mais propriedades<¦
EN: >Show more properties<¦

ES: 'Mostrar más propiedades ('¦
PT: 'Mostrar mais propriedades ('¦
EN: 'Show more properties ('¦

ES: >Buscar en esta zona<¦
PT: >Buscar nesta região<¦
EN: >Search this area<¦

ES: Buscar al mover el mapa¦
PT: Buscar ao mover o mapa¦
EN: Search as I move the map¦

ES: <span class="eyebrow" style="color:var(--gold-deep)">Para quien se aloja</span>¦
PT: <span class="eyebrow" style="color:var(--gold-deep)">Para quem se hospeda</span>¦
EN: <span class="eyebrow" style="color:var(--gold-deep)">For our guests</span>¦

ES: <h2>Tu estadía, <em>cuidada de punta a punta</em></h2>¦
PT: <h2>Sua estadia, <em>cuidada de ponta a ponta</em></h2>¦
EN: <h2>Your stay, <em>looked after from start to finish</em></h2>¦

ES: No somos una plataforma de anuncios: cada casa y cada apartamento que ves acá lo gestionamos nosotros, con un equipo propio en Punta del Este. Eso cambia cómo llegás, cómo encontrás la casa y quién te contesta cuando lo necesitás.¦
PT: Não somos uma plataforma de anúncios: cada casa e cada apartamento que você vê aqui é gerenciado por nós, com uma equipe própria em Punta del Este. Isso muda como você chega, como encontra a casa e quem responde quando você precisa.¦
EN: We are not an ad platform: every house and apartment you see here is managed by us, with our own team in Punta del Este. That changes how you arrive, how you find the house and who answers when you need help.¦

ES: alt="Entrega de llaves"¦
PT: alt="Entrega das chaves"¦
EN: alt="Key handover"¦

ES: alt="Equipo de Premium Host Punta"¦
PT: alt="Equipe da Premium Host Punta"¦
EN: alt="Premium Host Punta team"¦

ES: Hola%2C%20tengo%20una%20consulta%20sobre%20una%20reserva¦
PT: Ol%C3%A1%2C%20tenho%20uma%20d%C3%BAvida%20sobre%20uma%20reserva¦
EN: Hello%2C%20I%20have%20a%20question%20about%20a%20booking¦

ES: >¿Dudas? Escribinos por WhatsApp<¦
PT: >Dúvidas? Fale com a gente pelo WhatsApp<¦
EN: >Questions? Message us on WhatsApp<¦

ES: <h3>Precio claro desde el principio</h3>¦
PT: <h3>Preço claro desde o início</h3>¦
EN: <h3>Clear pricing from the start</h3>¦

ES: El total que ves ya incluye la limpieza final. Reservás online con el 50&nbsp;% y el saldo lo abonás antes de llegar. La política de cancelación está a la vista en cada propiedad, antes de pagar.¦
PT: O total que você vê já inclui a limpeza final. Você reserva online com 50&nbsp;% de sinal e paga o saldo antes de chegar. A política de cancelamento fica à vista em cada propriedade, antes de pagar.¦
EN: The total you see already includes the final cleaning. You book online with a 50&nbsp;% deposit and pay the balance before you arrive. The cancellation policy is shown on every property, before you pay.¦

ES: <h3>Llegada sin vueltas</h3>¦
PT: <h3>Chegada sem complicação</h3>¦
EN: <h3>A hassle-free arrival</h3>¦

ES: Antes de viajar recibís la guía de tu casa: cómo llegar, cómo entrar, wifi, normas y recomendaciones. En español, inglés o portugués.¦
PT: Antes de viajar você recebe o guia da sua casa: como chegar, como entrar, wifi, regras e recomendações. Em espanhol, inglês ou português.¦
EN: Before you travel you receive the guide to your home: how to get there, how to get in, wifi, house rules and recommendations. In Spanish, English or Portuguese.¦

ES: <h3>Limpieza con control</h3>¦
PT: <h3>Limpeza com controle</h3>¦
EN: <h3>Cleaning you can trust</h3>¦

ES: Cada limpieza sigue una lista por ambiente, con fotos de control, antes de que entres. Lo que ves en las fotos es lo que encontrás.¦
PT: Cada limpeza segue uma lista por ambiente, com fotos de controle, antes de você entrar. O que você vê nas fotos é o que encontra.¦
EN: Every cleaning follows a checklist room by room, with control photos, before you walk in. What you see in the photos is what you find.¦

ES: <h3>Personas, no un call center</h3>¦
PT: <h3>Pessoas, não um call center</h3>¦
EN: <h3>People, not a call center</h3>¦

ES: Te atiende nuestro equipo por WhatsApp antes, durante y después de tu estadía, en tu idioma.¦
PT: Nossa equipe atende você pelo WhatsApp antes, durante e depois da sua estadia, no seu idioma.¦
EN: Our team looks after you on WhatsApp before, during and after your stay, in your language.¦

ES: <h3>Un equipo en el lugar</h3>¦
PT: <h3>Uma equipe no local</h3>¦
EN: <h3>A team on the ground</h3>¦

ES: Estamos en Punta del Este. Si algo falla en la casa, lo coordina nuestro equipo de mantenimiento local, no alguien a miles de kilómetros.¦
PT: Estamos em Punta del Este. Se algo falhar na casa, quem resolve é a nossa equipe de manutenção local, não alguém a milhares de quilômetros.¦
EN: We are in Punta del Este. If something goes wrong in the house, our local maintenance team takes care of it, not someone thousands of kilometers away.¦

ES: <h3>Recomendaciones de quien vive acá</h3>¦
PT: <h3>Recomendações de quem mora aqui</h3>¦
EN: <h3>Tips from someone who lives here</h3>¦

ES: Playas, restaurantes y planes que conocemos de primera mano, en la guía de cada propiedad.¦
PT: Praias, restaurantes e programas que conhecemos de perto, no guia de cada propriedade.¦
EN: Beaches, restaurants and plans we know first hand, in the guide of each property.¦

ES: aria-label="Filtros"¦
PT: aria-label="Filtros"¦
EN: aria-label="Filters"¦

ES: <h3>Filtros</h3>¦
EN: <h3>Filters</h3>¦

ES: aria-label="Cerrar"¦
PT: aria-label="Fechar"¦
EN: aria-label="Close"¦

ES: <h4>Tipo de propiedad</h4>¦
PT: <h4>Tipo de propriedade</h4>¦
EN: <h4>Property type</h4>¦

ES: <h4>Dormitorios</h4>¦
PT: <h4>Dormitórios</h4>¦
EN: <h4>Bedrooms</h4>¦

ES: data-dorm="0">Cualquiera<¦
PT: data-dorm="0">Qualquer<¦
EN: data-dorm="0">Any<¦

ES: <h4>Reserva</h4>¦
EN: <h4>Booking</h4>¦

ES: ⚡ Reserva inmediata¦
PT: ⚡ Reserva imediata¦
EN: ⚡ Instant booking¦

ES: <h4>Comodidades</h4>¦
EN: <h4>Amenities</h4>¦

ES: id="fsLimpiar">Limpiar todo<¦
PT: id="fsLimpiar">Limpar tudo<¦
EN: id="fsLimpiar">Clear all<¦

ES: id="fsVer">Ver propiedades<¦
PT: id="fsVer">Ver propriedades<¦
EN: id="fsVer">View properties<¦

ES: id="fabTxt">Mapa<¦
EN: id="fabTxt">Map<¦

ES: 'Mapa'¦
EN: 'Map'¦

ES: 'Lista ('¦
EN: 'List ('¦

ES: Tocá el círculo de cada propiedad para sumarla¦
PT: Toque no círculo de cada propriedade para adicioná-la¦
EN: Tap the circle on each property to add it¦

ES: id="selSalir">Salir<¦
PT: id="selSalir">Sair<¦
EN: id="selSalir">Exit<¦

ES: Crear link de la selección¦
PT: Criar link da seleção¦
EN: Create selection link¦

ES: Crear link¦
PT: Criar link¦
EN: Create link¦

ES: Entrá con tu usuario de las plataformas de PHPunta.¦
PT: Entre com seu usuário das plataformas da PHPunta.¦
EN: Sign in with your PHPunta platforms username.¦

ES: >Usuario</label>¦
PT: >Usuário</label>¦
EN: >Username</label>¦

ES: >Contraseña</label>¦
PT: >Senha</label>¦
EN: >Password</label>¦

ES: >Cancelar<¦
PT: >Cancelar<¦
EN: >Cancel<¦

ES: id="lgOk">Entrar<¦
PT: id="lgOk">Entrar<¦
EN: id="lgOk">Sign in<¦

ES: >Cerrar<¦
PT: >Fechar<¦
EN: >Close<¦

ES: >Listo<¦
PT: >Concluir<¦
EN: >Done<¦

ES: >Quitar<¦
PT: >Remover<¦
EN: >Remove<¦

ES: >Mandar por WhatsApp<¦
PT: >Enviar por WhatsApp<¦
EN: >Send on WhatsApp<¦

ES: id="selCp">Copiar link<¦
PT: id="selCp">Copiar link<¦
EN: id="selCp">Copy link<¦

ES: 'Elegí la fecha de salida'¦
PT: 'Escolha a data de saída'¦
EN: 'Pick your check-out date'¦

ES: 'Elegí la fecha de llegada'¦
PT: 'Escolha a data de chegada'¦
EN: 'Pick your check-in date'¦

ES: aria-label="Mes anterior"¦
PT: aria-label="Mês anterior"¦
EN: aria-label="Previous month"¦

ES: aria-label="Mes siguiente"¦
PT: aria-label="Próximo mês"¦
EN: aria-label="Next month"¦

ES: >Borrar fechas<¦
PT: >Limpar datas<¦
EN: >Clear dates<¦

ES: const MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];¦
PT: const MESES = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'];¦
EN: const MESES = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];¦

ES: ['lu', 'ma', 'mi', 'ju', 'vi', 'sá', 'do']¦
PT: ['se', 'te', 'qu', 'qu', 'se', 'sá', 'do']¦
EN: ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']¦

ES: peninsula: 'Península'¦
EN: peninsula: 'Peninsula'¦

ES: mansa: 'Playa Mansa', brava: 'Playa Brava'¦
PT: mansa: 'Praia Mansa', brava: 'Praia Brava'¦

ES: d.getDate() + ' de ' + MESES[d.getMonth()] + ' de ' + d.getFullYear()¦
EN: MESES[d.getMonth()] + ' ' + d.getDate() + ', ' + d.getFullYear()¦

ES: d.getDate() + ' ' + MESES[d.getMonth()].slice(0, 3)¦
EN: MESES[d.getMonth()].slice(0, 3) + ' ' + d.getDate()¦

ES: ' · ' + MESES[d.getMonth()] + ' de ' + d.getFullYear() : ''¦
EN: ' · ' + MESES[d.getMonth()] + ' ' + d.getFullYear() : ''¦

ES: d + ' de ' + MESES[mo] + ': ' + tit¦
EN: MESES[mo] + ' ' + d + ': ' + tit¦

ES: ' noche'¦
PT: ' noite'¦
EN: ' night'¦

ES: ' noches'¦
PT: ' noites'¦
EN: ' nights'¦

ES: ' noches · '¦
PT: ' noites · '¦
EN: ' nights · '¦

ES: ' noches, '¦
PT: ' noites, '¦
EN: ' nights, '¦

ES: ' persona'¦
PT: ' pessoa'¦
EN: ' guest'¦

ES: ' personas'¦
PT: ' pessoas'¦
EN: ' guests'¦

ES: ' personas)</label>'¦
PT: ' pessoas)</label>'¦
EN: ' guests)</label>'¦

ES: ' bebé'¦
PT: ' bebê'¦
EN: ' infant'¦

ES: ' bebés'¦
PT: ' bebês'¦
EN: ' infants'¦

ES: ' propiedad'¦
PT: ' propriedade'¦
EN: ' property'¦

ES: ' propiedades'¦
PT: ' propriedades'¦
EN: ' properties'¦

ES: 'Ver '¦
EN: 'View '¦

ES: 'Sin resultados'¦
PT: 'Sem resultados'¦
EN: 'No results'¦

ES: No encontramos opciones con esos filtros¦
PT: Não encontramos opções com esses filtros¦
EN: We could not find options with those filters¦

ES: Probá con otra zona o menos filtros. Si buscás algo puntual, ¦
PT: Tente outra região ou menos filtros. Se você procura algo específico, ¦
EN: Try another area or fewer filters. If you are looking for something specific, ¦

ES: >escribinos por WhatsApp</a> y te ayudamos.</p>¦
PT: >fale com a gente pelo WhatsApp</a> e ajudamos você.</p>¦
EN: >message us on WhatsApp</a> and we will help you.</p>¦

ES: No pudimos cargar las propiedades¦
PT: Não conseguimos carregar as propriedades¦
EN: We could not load the properties¦

ES: Probá recargar la página en un momento, o escribinos por <a¦
PT: Tente recarregar a página em instantes ou fale com a gente pelo <a¦
EN: Try reloading the page in a moment, or message us on <a¦

ES: No hay propiedades en esta zona¦
PT: Não há propriedades nesta região¦
EN: There are no properties in this area¦

ES: Mové el mapa o alejá el zoom.¦
PT: Mova o mapa ou diminua o zoom.¦
EN: Move the map or zoom out.¦

ES: Consultá precio y disponibilidad¦
PT: Consulte preço e disponibilidade¦
EN: Ask for price and availability¦

ES: Ya no está disponible en esas fechas¦
PT: Não está mais disponível nessas datas¦
EN: No longer available on those dates¦

ES: <span class="no">Mínimo ¦
EN: <span class="no">Minimum ¦

ES: ' noches para esa llegada</span>'¦
PT: ' noites para essa chegada</span>'¦
EN: ' nights for that check-in</span>'¦

ES: <span class="no">Recibe hasta ¦
PT: <span class="no">Recebe até ¦
EN: <span class="no">Sleeps up to ¦

ES: ' huéspedes</span>'¦
PT: ' hóspedes</span>'¦
EN: ' guests</span>'¦

ES: Sin fechas online · consultanos¦
PT: Sem datas online · consulte-nos¦
EN: No dates online · ask us¦

ES: Precio a confirmar por WhatsApp¦
PT: Preço a confirmar pelo WhatsApp¦
EN: Price to be confirmed on WhatsApp¦

ES: No disponible en esas fechas¦
PT: Indisponível nessas datas¦
EN: Not available on those dates¦

ES: Consultá el precio para esas fechas¦
PT: Consulte o preço para essas datas¦
EN: Ask for the price for those dates¦

ES: Consultá disponibilidad¦
PT: Consulte a disponibilidade¦
EN: Ask about availability¦

ES: Elegí tus fechas para ver el precio¦
PT: Escolha as datas para ver o preço¦
EN: Pick your dates to see the price¦

ES: ' · limpieza incluida</small>'¦
PT: ' · limpeza incluída</small>'¦
EN: ' · cleaning included</small>'¦

ES: 'Casa'¦
EN: 'House'¦

ES: 'Apartamento'¦
EN: 'Apartment'¦

ES: ' dormitorio'¦
PT: ' dormitório'¦
EN: ' bedroom'¦

ES: ' dormitorios'¦
PT: ' dormitórios'¦
EN: ' bedrooms'¦

ES: 'hasta '¦
PT: 'até '¦
EN: 'up to '¦

ES: ' huéspedes'¦
PT: ' hóspedes'¦
EN: ' guests'¦

ES: 'Frente al mar'¦
PT: 'Frente para o mar'¦
EN: 'Oceanfront'¦

ES: 'Cerca de la playa'¦
PT: 'Perto da praia'¦
EN: 'Near the beach'¦

ES: 'Piscina'¦
EN: 'Pool'¦

ES: 'Parrillero'¦
PT: 'Churrasqueira'¦
EN: 'BBQ grill'¦

ES: aria-label="Foto anterior"¦
PT: aria-label="Foto anterior"¦
EN: aria-label="Previous photo"¦

ES: aria-label="Foto siguiente"¦
PT: aria-label="Próxima foto"¦
EN: aria-label="Next photo"¦

ES: ph-tag">Frente al mar<¦
PT: ph-tag">Frente para o mar<¦
EN: ph-tag">Oceanfront<¦

ES: aria-label="Sumar a la selección"¦
PT: aria-label="Adicionar à seleção"¦
EN: aria-label="Add to selection"¦

ES: 'No disp.'¦
PT: 'Indisp.'¦
EN: 'Unavail.'¦

ES: 'Armando…'¦
PT: 'Montando…'¦
EN: 'Building…'¦

ES: 'Armando selección…'¦
PT: 'Montando seleção…'¦
EN: 'Building selection…'¦

ES: 'Selección'¦
PT: 'Seleção'¦
EN: 'Selection'¦

ES: 'Armar selección'¦
PT: 'Montar seleção'¦
EN: 'Build a selection'¦

ES: ' propiedad seleccionada'¦
PT: ' propriedade selecionada'¦
EN: ' property selected'¦

ES: ' propiedades seleccionadas'¦
PT: ' propriedades selecionadas'¦
EN: ' properties selected'¦

ES: 'Una selección puede tener hasta 12 propiedades.'¦
PT: 'Uma seleção pode ter até 12 propriedades.'¦
EN: 'A selection can have up to 12 properties.'¦

ES: 'Usuario o contraseña incorrectos.'¦
PT: 'Usuário ou senha incorretos.'¦
EN: 'Incorrect username or password.'¦

ES: 'Elegí al menos una propiedad tocando su círculo.'¦
PT: 'Escolha pelo menos uma propriedade tocando no círculo dela.'¦
EN: 'Choose at least one property by tapping its circle.'¦

ES: id="selConF" checked /> Con fechas: ¦
PT: id="selConF" checked /> Com datas: ¦
EN: id="selConF" checked /> With dates: ¦

ES: <p class="nota">Sin fechas: el interesado ve las propiedades y elige las fechas en cada una. Para mandarla con fechas y precios, elegí las fechas arriba antes de crear el link.</p>¦
PT: <p class="nota">Sem datas: o interessado vê as propriedades e escolhe as datas em cada uma. Para enviar com datas e preços, escolha as datas acima antes de criar o link.</p>¦
EN: <p class="nota">No dates: the guest sees the properties and picks the dates on each one. To send it with dates and prices, pick the dates above before creating the link.</p>¦

ES: <label>Título (opcional)</label>¦
PT: <label>Título (opcional)</label>¦
EN: <label>Title (optional)</label>¦

ES: placeholder="Opciones para tu estadía en enero"¦
PT: placeholder="Opções para sua estadia em janeiro"¦
EN: placeholder="Options for your stay in January"¦

ES: <label>Nota para el interesado (opcional)</label>¦
PT: <label>Nota para o interessado (opcional)</label>¦
EN: <label>Note for the guest (optional)</label>¦

ES: 'Calculando precios…'¦
PT: 'Calculando preços…'¦
EN: 'Calculating prices…'¦

ES: 'Creando…'¦
PT: 'Criando…'¦
EN: 'Creating…'¦

ES: 'No se pudo crear el link.'¦
PT: 'Não foi possível criar o link.'¦
EN: 'The link could not be created.'¦

ES: <label>Link listo para mandar</label>¦
PT: <label>Link pronto para enviar</label>¦
EN: <label>Link ready to send</label>¦

ES: 'Copiado ✓'¦
PT: 'Copiado ✓'¦
EN: 'Copied ✓'¦

ES: 'Copiá el link:'¦
PT: 'Copie o link:'¦
EN: 'Copy the link:'¦

ES: 'Hola! Vi la selección de propiedades que me mandaron: '¦
PT: 'Olá! Vi a seleção de propriedades que me enviaram: '¦
EN: 'Hello! I saw the selection of properties you sent me: '¦

ES: 'Selección de propiedades'¦
PT: 'Seleção de propriedades'¦
EN: 'Selection of properties'¦

ES: ', de PHPunta'¦
PT: ', da PHPunta'¦
EN: ', at PHPunta'¦

ES: ' · de '¦
EN: ' · from '¦

ES: 'Opciones <em>para vos</em>'¦
PT: 'Opções <em>para você</em>'¦
EN: 'Options <em>for you</em>'¦

ES: 'Las fechas de esta selección ya pasaron: elegí nuevas fechas en cada propiedad.'¦
PT: 'As datas desta seleção já passaram: escolha novas datas em cada propriedade.'¦
EN: 'The dates of this selection have passed: pick new dates on each property.'¦

ES: 'Del '¦
PT: 'De '¦
EN: 'From '¦

ES: ' al '¦
PT: ' a '¦
EN: ' to '¦

ES: '. Los precios son finales, con la limpieza incluida.'¦
PT: '. Os preços são finais, com a limpeza incluída.'¦
EN: '. Prices are final, with cleaning included.'¦

ES: 'Elegí las fechas en cada propiedad para ver disponibilidad y precio final.'¦
PT: 'Escolha as datas em cada propriedade para ver a disponibilidade e o preço final.'¦
EN: 'Pick the dates on each property to see availability and the final price.'¦

ES: Ver todas nuestras propiedades¦
PT: Ver todas as nossas propriedades¦
EN: See all our properties¦

ES: ' propiedad de esta selección ya no está disponible.'¦
PT: ' propriedade desta seleção não está mais disponível.'¦
EN: ' property of this selection is no longer available.'¦

ES: ' propiedades de esta selección ya no están disponibles.'¦
PT: ' propriedades desta seleção não estão mais disponíveis.'¦
EN: ' properties of this selection are no longer available.'¦

ES: 'Esta selección no existe o ya no está disponible'¦
PT: 'Esta seleção não existe ou não está mais disponível'¦
EN: 'This selection does not exist or is no longer available'¦

ES: 'No pudimos cargar la selección'¦
PT: 'Não conseguimos carregar a seleção'¦
EN: 'We could not load the selection'¦

ES: 'Sin fechas online'¦
PT: 'Sem datas online'¦
EN: 'No dates online'¦

ES: Sin fechas online¦
PT: Sem datas online¦
EN: No dates online¦

ES: Consultanos por WhatsApp: te contamos cuándo se libera o te pasamos opciones parecidas.¦
PT: Fale com a gente pelo WhatsApp: avisamos quando liberar ou indicamos opções parecidas.¦
EN: Message us on WhatsApp: we will tell you when it opens up or suggest similar options.¦

ES: <div class="aviso">Elegí las fechas en el calendario para ver el precio final.</div>¦
PT: <div class="aviso">Escolha as datas no calendário para ver o preço final.</div>¦
EN: <div class="aviso">Pick your dates in the calendar to see the final price.</div>¦

ES: Calculando el precio…¦
PT: Calculando o preço…¦
EN: Calculating the price…¦

ES: <span>Precio sin descuento</span>¦
PT: <span>Preço sem desconto</span>¦
EN: <span>Price without discount</span>¦

ES: <span>Descuento por estadía de ¦
PT: <span>Desconto por estadia de ¦
EN: <span>Discount for a ¦

ES: ' noches</span><span class="menos">−'¦
PT: ' noites</span><span class="menos">−'¦
EN: '-night stay</span><span class="menos">−'¦

ES: <span>Total por ¦
PT: <span>Total por ¦
EN: <span>Total for ¦

ES: Incluye la tarifa de limpieza.¦
PT: Inclui a taxa de limpeza.¦
EN: Includes the cleaning fee.¦

ES: Esta misma propiedad en otras plataformas te hubiera costado hasta <b>¦
PT: Esta mesma propriedade em outras plataformas teria custado até <b>¦
EN: This same property on other platforms would have cost you up to <b>¦

ES: Esas fechas no están disponibles.¦
PT: Essas datas não estão disponíveis.¦
EN: Those dates are not available.¦

ES: Libres cerca: ¦
PT: Livres por perto: ¦
EN: Free nearby: ¦

ES: Para esa llegada la estadía mínima es de ¦
PT: Para essa chegada, a estadia mínima é de ¦
EN: For that check-in the minimum stay is ¦

ES: ' noches.</div>'¦
PT: ' noites.</div>'¦
EN: ' nights.</div>'¦

ES: Esta propiedad recibe hasta ¦
PT: Esta propriedade recebe até ¦
EN: This property sleeps up to ¦

ES: ' huéspedes.</div>'¦
PT: ' hóspedes.</div>'¦
EN: ' guests.</div>'¦

ES: Para estadías largas armamos una propuesta a medida. Escribinos y te la pasamos.¦
PT: Para estadias longas montamos uma proposta sob medida. Escreva para nós e enviamos.¦
EN: For long stays we put together a tailor-made proposal. Message us and we will send it to you.¦

ES: No pudimos calcular el precio.¦
PT: Não conseguimos calcular o preço.¦
EN: We could not calculate the price.¦

ES: Para esas fechas confirmamos el precio por WhatsApp en minutos.¦
PT: Para essas datas confirmamos o preço pelo WhatsApp em minutos.¦
EN: For those dates we confirm the price on WhatsApp within minutes.¦

ES: <span>Al reservar pagás el total</span>¦
PT: <span>Ao reservar você paga o total</span>¦
EN: <span>You pay the full amount when booking</span>¦

ES: <span>Al reservar (¦
PT: <span>Ao reservar (¦
EN: <span>When booking (¦

ES: <span>Saldo¦
PT: <span>Saldo¦
EN: <span>Balance¦

ES: ', hasta el '¦
PT: ', até '¦
EN: ', due by '¦

ES: <span>Garantía (se devuelve)</span>¦
PT: <span>Caução (reembolsável)</span>¦
EN: <span>Security deposit (refundable)</span>¦

ES: <b>Política de cancelación</b>¦
PT: <b>Política de cancelamento</b>¦
EN: <b>Cancellation policy</b>¦

ES: >Consultar por WhatsApp</a>¦
PT: >Consultar pelo WhatsApp</a>¦
EN: >Ask on WhatsApp</a>¦

ES: 'Consultar por WhatsApp'¦
PT: 'Consultar pelo WhatsApp'¦
EN: 'Ask on WhatsApp'¦

ES: Reserva inmediata: pagás la seña online con tarjeta u otros medios.¦
PT: Reserva imediata: você paga o sinal online com cartão ou outros meios.¦
EN: Instant booking: you pay the deposit online by card or other methods.¦

ES: 'Por la cercanía de la fecha, esta reserva se hace por solicitud. '¦
PT: 'Como a data está próxima, esta reserva é feita por solicitação. '¦
EN: 'Because the date is close, this booking is made by request. '¦

ES: 'No se te cobra nada todavía: el equipo confirma la disponibilidad y te manda el link de pago.'¦
PT: 'Nada é cobrado ainda: a equipe confirma a disponibilidade e envia o link de pagamento.'¦
EN: 'You are not charged anything yet: the team confirms availability and sends you the payment link.'¦

ES: 'Solicitar reserva'¦
PT: 'Solicitar reserva'¦
EN: 'Request to book'¦

ES: 'Elegí tus fechas'¦
PT: 'Escolha as datas'¦
EN: 'Pick your dates'¦

ES: >¿Dudas? Escribinos por WhatsApp<¦
PT: >Dúvidas? Fale com a gente pelo WhatsApp<¦
EN: >Questions? Message us on WhatsApp<¦
'''

_DATOS_FICHA = r'''
ES: Reserva inmediata</div>¦
PT: Reserva imediata</div>¦
EN: Instant booking</div>¦

ES: 'Salida posible'¦
PT: 'Saída possível'¦
EN: 'Check-out possible'¦

ES: 'Hay noches ocupadas antes: tocalo para empezar una nueva llegada'¦
PT: 'Há noites ocupadas antes: toque para começar uma nova chegada'¦
EN: 'There are booked nights before: tap to start a new check-in'¦

ES: 'No disponible'¦
PT: 'Indisponível'¦
EN: 'Not available'¦

ES: 'Disponible'¦
PT: 'Disponível'¦
EN: 'Available'¦

ES: 'Solo como día de salida'¦
PT: 'Só como dia de saída'¦
EN: 'Check-out day only'¦

ES: 'Llegada '¦
PT: 'Chegada '¦
EN: 'Check-in '¦

ES: ' · ahora elegí la <b>salida</b>'¦
PT: ' · agora escolha a <b>saída</b>'¦
EN: ' · now pick your <b>check-out</b>'¦

ES: ' (podés salir hasta el '¦
PT: ' (você pode sair até '¦
EN: ' (you can check out until '¦

ES: 'Elegí tu <b>llegada</b> y después tu <b>salida</b>'¦
PT: 'Escolha sua <b>chegada</b> e depois sua <b>saída</b>'¦
EN: 'Pick your <b>check-in</b> and then your <b>check-out</b>'¦

ES: 'El '¦
PT: 'O dia '¦
EN: 'On '¦

ES: ' entra otro grupo: ese día solo sirve como <b>salida</b>. Elegí primero tu llegada.'¦
PT: ' entra outro grupo: esse dia só serve como <b>saída</b>. Escolha primeiro a sua chegada.'¦
EN: ' another group arrives: that day only works as a <b>check-out</b> day. Pick your check-in first.'¦

ES: ' libres'¦
PT: ' livres'¦
EN: ' free'¦

ES: 'completo'¦
PT: 'lotado'¦
EN: 'full'¦

ES: aria-label="Ir a un mes"¦
PT: aria-label="Ir para um mês"¦
EN: aria-label="Go to a month"¦

ES: <i class="lg lib"></i>Disponible<i class="lg ocup"></i>No disponible<i class="lg sal"></i>Solo salida¦
PT: <i class="lg lib"></i>Disponível<i class="lg ocup"></i>Indisponível<i class="lg sal"></i>Só saída¦
EN: <i class="lg lib"></i>Available<i class="lg ocup"></i>Not available<i class="lg sal"></i>Check-out only¦

ES: </b>huéspedes</span>¦
PT: </b>hóspedes</span>¦
EN: </b>guests</span>¦

ES: 'dormitorio'¦
PT: 'dormitório'¦
EN: 'bedroom'¦

ES: 'dormitorios'¦
PT: 'dormitórios'¦
EN: 'bedrooms'¦

ES: 'baño'¦
PT: 'banheiro'¦
EN: 'bathroom'¦

ES: 'baños'¦
PT: 'banheiros'¦
EN: 'bathrooms'¦

ES: ' — foto '¦
PT: ' — foto '¦
EN: ' — photo '¦

ES: id="galTodas">Ver las ¦
PT: id="galTodas">Ver todas as ¦
EN: id="galTodas">Show all ¦

ES: ' fotos</button>'¦
EN: ' photos</button>'¦

ES: 'Mostrar más'¦
PT: 'Mostrar mais'¦
EN: 'Show more'¦

ES: >Mostrar más<¦
PT: >Mostrar mais<¦
EN: >Show more<¦

ES: 'Mostrar menos'¦
PT: 'Mostrar menos'¦
EN: 'Show less'¦

ES: <h2>La propiedad</h2>¦
PT: <h2>A propriedade</h2>¦
EN: <h2>The property</h2>¦

ES: <h2>Dónde vas a dormir</h2>¦
PT: <h2>Onde você vai dormir</h2>¦
EN: <h2>Where you will sleep</h2>¦

ES: 'Ropa de cama y toallas'¦
PT: 'Roupa de cama e toalhas'¦
EN: 'Bed linens and towels'¦

ES: <h2>Qué ofrece este lugar</h2>¦
PT: <h2>O que este lugar oferece</h2>¦
EN: <h2>What this place offers</h2>¦

ES: id="amenMas">Mostrar las ¦
PT: id="amenMas">Mostrar todas as ¦
EN: id="amenMas">Show all ¦

ES: 'Mostrar las '¦
PT: 'Mostrar todas as '¦
EN: 'Show all '¦

ES: ' comodidades</button>'¦
PT: ' comodidades</button>'¦
EN: ' amenities</button>'¦

ES: ' comodidades'¦
PT: ' comodidades'¦
EN: ' amenities'¦

ES: 'Limpieza'¦
PT: 'Limpeza'¦
EN: 'Cleanliness'¦

ES: 'Veracidad'¦
PT: 'Veracidade'¦
EN: 'Accuracy'¦

ES: 'Llegada'¦
PT: 'Chegada'¦
EN: 'Check-in'¦

ES: 'Comunicación'¦
PT: 'Comunicação'¦
EN: 'Communication'¦

ES: 'Ubicación'¦
PT: 'Localização'¦
EN: 'Location'¦

ES: 'Calidad-precio'¦
PT: 'Custo-benefício'¦
EN: 'Value'¦

ES: <h2>Algunas reseñas de la propiedad</h2>¦
PT: <h2>Algumas avaliações da propriedade</h2>¦
EN: <h2>Some reviews of the property</h2>¦

ES: aria-label="Anterior"¦
PT: aria-label="Anterior"¦
EN: aria-label="Previous"¦

ES: aria-label="Siguiente"¦
PT: aria-label="Seguinte"¦
EN: aria-label="Next"¦

ES: <h2>Hacé preguntas sobre este alojamiento</h2>¦
PT: <h2>Faça perguntas sobre esta hospedagem</h2>¦
EN: <h2>Ask questions about this property</h2>¦

ES: placeholder="Haz cualquier pregunta sobre esta propiedad"¦
PT: placeholder="Faça qualquer pergunta sobre esta propriedade"¦
EN: placeholder="Ask anything about this property"¦

ES: id="pregB">Preguntar<¦
PT: id="pregB">Perguntar<¦
EN: id="pregB">Ask<¦

ES: '¿Hay estacionamiento?'¦
PT: 'Tem estacionamento?'¦
EN: 'Is there parking?'¦

ES: '¿Qué tan cerca está la playa?'¦
PT: 'Quão perto fica a praia?'¦
EN: 'How close is the beach?'¦

ES: '¿Se aceptan mascotas?'¦
PT: 'Aceitam animais de estimação?'¦
EN: 'Are pets allowed?'¦

ES: '¿Tiene aire acondicionado?'¦
PT: 'Tem ar-condicionado?'¦
EN: 'Does it have air conditioning?'¦

ES: Responde un asistente con IA según la información de esta página. Para confirmar algo puntual, escribinos por WhatsApp.¦
PT: Quem responde é um assistente com IA, com base nas informações desta página. Para confirmar algo específico, fale com a gente pelo WhatsApp.¦
EN: An AI assistant answers based on the information on this page. To confirm something specific, message us on WhatsApp.¦

ES: <span>Mascotas</span><b>¦
PT: <span>Animais de estimação</span><b>¦
EN: <span>Pets</span><b>¦

ES: 'Se aceptan'¦
PT: 'Aceitos'¦
EN: 'Allowed'¦

ES: 'No se aceptan'¦
PT: 'Não aceitos'¦
EN: 'Not allowed'¦

ES: Compartir</button>¦
PT: Compartilhar</button>¦
EN: Share</button>¦

ES: Por ahora esta propiedad no tiene fechas abiertas para reservar online. Escribinos por WhatsApp y te avisamos cuando se libere, o te recomendamos opciones parecidas.¦
PT: Por enquanto esta propriedade não tem datas abertas para reservar online. Escreva para nós pelo WhatsApp e avisamos quando liberar, ou indicamos opções parecidas.¦
EN: This property has no dates open for online booking right now. Message us on WhatsApp and we will let you know when it opens up, or recommend similar options.¦

ES: <h2>Disponibilidad</h2>¦
PT: <h2>Disponibilidade</h2>¦
EN: <h2>Availability</h2>¦

ES: Nuestros calendarios están actualizados en tiempo real.¦
PT: Nossos calendários são atualizados em tempo real.¦
EN: Our calendars are updated in real time.¦

ES: <h2>Bueno saber</h2>¦
PT: <h2>Bom saber</h2>¦
EN: <h2>Good to know</h2>¦

ES: <span>Entrada</span><b>Desde las ¦
PT: <span>Check-in</span><b>A partir das ¦
EN: <span>Check-in</span><b>From ¦

ES: <span>Salida</span><b>Hasta las ¦
PT: <span>Check-out</span><b>Até às ¦
EN: <span>Check-out</span><b>Until ¦

ES: <span>Estadía mínima</span><b>¦
PT: <span>Estadia mínima</span><b>¦
EN: <span>Minimum stay</span><b>¦

ES: ' noches</b></div>'¦
PT: ' noites</b></div>'¦
EN: ' nights</b></div>'¦

ES: <span>Pago</span><b>¦
PT: <span>Pagamento</span><b>¦
EN: <span>Payment</span><b>¦

ES: '% al reservar</b></div>'¦
PT: '% ao reservar</b></div>'¦
EN: '% when booking</b></div>'¦

ES: Se reserva con el ¦
PT: Reserva-se com ¦
EN: You book with a ¦

ES: % y el saldo se paga antes de la llegada (7 días antes en temporada alta, 3 días antes en temporada baja). La garantía se devuelve después de la salida, una vez revisada la propiedad. La estadía mínima puede cambiar según la fecha.</p></div>¦
PT: % de sinal e o saldo é pago antes da chegada (7 dias antes na alta temporada, 3 dias antes na baixa temporada). A caução é devolvida depois da saída, depois de revisada a propriedade. A estadia mínima pode mudar conforme a data.</p></div>¦
EN: % deposit and the balance is paid before arrival (7 days before in high season, 3 days before in low season). The security deposit is refunded after check-out, once the property has been checked. The minimum stay may change depending on the date.</p></div>¦

ES: <h2>Política de cancelación</h2>¦
PT: <h2>Política de cancelamento</h2>¦
EN: <h2>Cancellation policy</h2>¦

ES: <b>Temporada alta · estadías con alguna noche del 15 de diciembre a fin de febrero</b>Se reserva con el 50%, que no es reembolsable. Tenés 48 horas para arrepentirte, siempre que falten 30 días o más para tu llegada. El saldo se paga 7 días antes de la llegada y no es reembolsable. Si una sola noche de tu estadía cae en temporada alta, esta política se aplica a toda la reserva.¦
PT: <b>Alta temporada · estadias com alguma noite entre 15 de dezembro e o fim de fevereiro</b>Reserva-se com 50%, que não é reembolsável. Você tem 48 horas para desistir, desde que faltem 30 dias ou mais para a sua chegada. O saldo é pago 7 dias antes da chegada e não é reembolsável. Se uma única noite da sua estadia cair na alta temporada, esta política vale para toda a reserva.¦
EN: <b>High season · stays with any night from December 15 to the end of February</b>You book with 50%, which is non-refundable. You have 48 hours to change your mind, as long as your arrival is 30 days or more away. The balance is paid 7 days before arrival and is non-refundable. If even one night of your stay falls in high season, this policy applies to the whole booking.¦

ES: <b>Temporada baja · estadías que no tocan esas fechas</b>Se reserva con el 50%, que te devolvemos si cancelás hasta 30 días antes de la llegada. El saldo se paga 3 días antes de la llegada y no es reembolsable.¦
PT: <b>Baixa temporada · estadias que não tocam essas datas</b>Reserva-se com 50%, que devolvemos se você cancelar até 30 dias antes da chegada. O saldo é pago 3 dias antes da chegada e não é reembolsável.¦
EN: <b>Low season · stays that do not touch those dates</b>You book with 50%, which we refund if you cancel up to 30 days before arrival. The balance is paid 3 days before arrival and is non-refundable.¦

ES: Al elegir tus fechas te mostramos los plazos exactos de tu estadía antes de pagar.¦
PT: Ao escolher as datas, mostramos os prazos exatos da sua estadia antes de pagar.¦
EN: When you pick your dates we show you the exact deadlines for your stay before you pay.¦

ES: <h2>Dónde vas a estar</h2>¦
PT: <h2>Onde você vai ficar</h2>¦
EN: <h2>Where you will be</h2>¦

ES: Hacé clic en una categoría para ver nuestras recomendaciones.¦
PT: Clique em uma categoria para ver as nossas recomendações.¦
EN: Click a category to see our recommendations.¦

ES: 'Ubicación aproximada. La dirección exacta se envía al confirmar la reserva.'¦
PT: 'Localização aproximada. O endereço exato é enviado ao confirmar a reserva.'¦
EN: 'Approximate location. The exact address is sent once the booking is confirmed.'¦

ES: 'La dirección exacta se envía al confirmar la reserva.'¦
PT: 'O endereço exato é enviado ao confirmar a reserva.'¦
EN: 'The exact address is sent once the booking is confirmed.'¦

ES: ' Las distancias son en línea recta.</p>¦
PT: ' As distâncias são em linha reta.</p>¦
EN: ' Distances are in a straight line.</p>¦

ES: id="mbarB">Ver precio</button>¦
PT: id="mbarB">Ver preço</button>¦
EN: id="mbarB">See price</button>¦

ES: 'Leer más'¦
PT: 'Ler mais'¦
EN: 'Read more'¦

ES: 'Leer menos'¦
PT: 'Ler menos'¦
EN: 'Read less'¦

ES: ' · del '¦
PT: ' · de '¦
EN: ' · from '¦

ES: ' del '¦
PT: ' de '¦
EN: ' from '¦

ES: 'Link copiado. Ya lo podés pegar donde quieras.'¦
PT: 'Link copiado. Agora você pode colar onde quiser.'¦
EN: 'Link copied. You can now paste it wherever you like.'¦

ES: <button type="button" data-c="1">Con estas fechas (¦
PT: <button type="button" data-c="1">Com estas datas (¦
EN: <button type="button" data-c="1">With these dates (¦

ES: Solo la propiedad, sin fechas¦
PT: Só a propriedade, sem datas¦
EN: Just the property, no dates¦

ES: 'Pensando…'¦
PT: 'Pensando…'¦
EN: 'Thinking…'¦

ES: 'No pude responder ahora.'¦
PT: 'Não consegui responder agora.'¦
EN: 'I could not answer right now.'¦

ES: 'No pude responder ahora. Escribinos por WhatsApp.'¦
PT: 'Não consegui responder agora. Escreva para nós pelo WhatsApp.'¦
EN: 'I could not answer right now. Message us on WhatsApp.'¦

ES: function distTxt(km) { return km < 1 ? 'a ' + (Math.round(km * 10) * 100) + ' m' : 'a ' + String(km < 10 ? km.toFixed(1) : Math.round(km)).replace('.', ',') + ' km'; }¦
EN: function distTxt(km) { return km < 1 ? (Math.round(km * 10) * 100) + ' m away' : String(km < 10 ? km.toFixed(1) : Math.round(km)) + ' km away'; }¦

ES: '★ ' + String(x.rating).replace('.', ',')¦
EN: '★ ' + String(x.rating)¦

ES: Consultanos por WhatsApp: te contamos cuándo se libera o te pasamos opciones parecidas.¦
PT: Fale com a gente pelo WhatsApp: avisamos quando liberar ou indicamos opções parecidas.¦
EN: Message us on WhatsApp: we will tell you when it opens up or suggest similar options.¦

ES: 'Consultar'¦
PT: 'Consultar'¦
EN: 'Inquire'¦

ES: 'Elegí tus fechas<br><small>para ver el precio</small>'¦
PT: 'Escolha as datas<br><small>para ver o preço</small>'¦
EN: 'Pick your dates<br><small>to see the price</small>'¦

ES: <span>Llegada</span><div>¦
PT: <span>Chegada</span><div>¦
EN: <span>Check-in</span><div>¦

ES: <span>Salida</span><div>¦
PT: <span>Saída</span><div>¦
EN: <span>Check-out</span><div>¦

ES: 'Agregar'¦
PT: 'Adicionar'¦
EN: 'Add'¦

ES: <span>Huéspedes</span><div>¦
PT: <span>Hóspedes</span><div>¦
EN: <span>Guests</span><div>¦

ES: padding-top:4px">Máximo ¦
PT: padding-top:4px">Máximo ¦
EN: padding-top:4px">Maximum ¦

ES: ' huéspedes.</p></div>'¦
PT: ' hóspedes.</p></div>'¦
EN: ' guests.</p></div>'¦

ES: 'Reservar'¦
PT: 'Reservar'¦
EN: 'Book'¦

ES: 'Solicitar'¦
PT: 'Solicitar'¦
EN: 'Request'¦

ES: 'Ver fechas'¦
PT: 'Ver datas'¦
EN: 'See dates'¦

ES: 'Hola! Me interesa '¦
PT: 'Olá! Tenho interesse em '¦
EN: 'Hello! I am interested in '¦

ES: ' y '¦
PT: ' e '¦
EN: ' and '¦

ES: ' (incluye la limpieza) · '¦
PT: ' (limpeza incluída) · '¦
EN: ' (cleaning included) · '¦

ES: url: '/condiciones-reserva.html', tit: 'Bases y condiciones de la reserva'¦
PT: url: '/pt/condicoes-reserva.html', tit: 'Bases e condições da reserva'¦
EN: url: '/en/booking-terms.html', tit: 'Booking terms and conditions'¦

ES: url: '/reglas-de-la-casa.html', tit: 'Reglas de la casa'¦
PT: url: '/pt/regras-da-casa.html', tit: 'Regras da casa'¦
EN: url: '/en/house-rules.html', tit: 'House rules'¦

ES: Antes de reservar¦
PT: Antes de reservar¦
EN: Before you book¦

ES: Ver las reglas completas¦
PT: Ver as regras completas¦
EN: See the full rules¦

ES: >Aceptar<¦
PT: >Aceitar<¦
EN: >Accept<¦

ES: Cargando…¦
PT: Carregando…¦
EN: Loading…¦

ES: Abrir en una página aparte¦
PT: Abrir em uma página separada¦
EN: Open on a separate page¦

ES: No pudimos cargar el texto acá. <a href="¦
PT: Não conseguimos carregar o texto aqui. <a href="¦
EN: We could not load the text here. <a href="¦

ES: >Abrilo en una página aparte</a>.¦
PT: >Abra em uma página separada</a>.¦
EN: >Open it on a separate page</a>.¦

ES: 'Tu reserva'¦
PT: 'Sua reserva'¦
EN: 'Your booking'¦

ES: 'Solicitud de reserva'¦
PT: 'Solicitação de reserva'¦
EN: 'Booking request'¦

ES: ' huésped'¦
PT: ' hóspede'¦
EN: ' guest'¦

ES: 'pagás el total ahora'¦
PT: 'você paga o total agora'¦
EN: 'you pay the full amount now'¦

ES: 'ahora pagás '¦
PT: 'agora você paga '¦
EN: 'you pay now '¦

ES: 'no pagás nada ahora. Si el equipo la aprueba, te manda el link para pagar '¦
PT: 'você não paga nada agora. Se a equipe aprovar, ela envia o link para pagar '¦
EN: 'you pay nothing now. If the team approves it, it will send you the link to pay '¦

ES: 'el total'¦
PT: 'o total'¦
EN: 'the full amount'¦

ES: 'la seña de '¦
PT: 'o sinal de '¦
EN: 'the deposit of '¦

ES: <label for="rN">Nombre y apellido</label>¦
PT: <label for="rN">Nome e sobrenome</label>¦
EN: <label for="rN">Full name</label>¦

ES: <label for="rT">Teléfono (WhatsApp, con código de país)</label>¦
PT: <label for="rT">Telefone (WhatsApp, com código do país)</label>¦
EN: <label for="rT">Phone (WhatsApp, with country code)</label>¦

ES: <label for="rM">Mensaje para el equipo (opcional)</label>¦
PT: <label for="rM">Mensagem para a equipe (opcional)</label>¦
EN: <label for="rM">Message for the team (optional)</label>¦

ES: placeholder="Contanos quiénes viajan y cualquier pedido especial."¦
PT: placeholder="Conte quem vai viajar e qualquer pedido especial."¦
EN: placeholder="Tell us who is traveling and any special request."¦

ES: Leí y acepto la política de cancelación.¦
PT: Li e aceito a política de cancelamento.¦
EN: I have read and accept the cancellation policy.¦

ES: Leí y acepto las <button type="button" class="lnk" data-doc="bases">¦
PT: Li e aceito as <button type="button" class="lnk" data-doc="bases">¦
EN: I have read and accept the <button type="button" class="lnk" data-doc="bases">¦

ES: bases y condiciones</button> de la reserva.¦
PT: bases e condições</button> da reserva.¦
EN: booking terms and conditions</button>.¦

ES: Leí y acepto las <button type="button" class="lnk" data-doc="reglas">¦
PT: Li e aceito as <button type="button" class="lnk" data-doc="reglas">¦
EN: I have read and accept the <button type="button" class="lnk" data-doc="reglas">¦

ES: reglas de la casa</button>.¦
PT: regras da casa</button>.¦
EN: house rules</button>.¦

ES: >Volver<¦
PT: >Voltar<¦
EN: >Back<¦

ES: 'Ir a pagar '¦
PT: 'Pagar '¦
EN: 'Pay '¦

ES: 'Enviar solicitud'¦
PT: 'Enviar solicitação'¦
EN: 'Send request'¦

ES: 'El pago se hace en una página segura de nuestro procesador de pagos (dLocal); tus datos de tarjeta no pasan por nosotros. Después del pago, el equipo de reservas te confirma la reserva por WhatsApp o email. Si por algún motivo no se pudiera confirmar, te devolvemos el 100%.'¦
PT: 'O pagamento é feito em uma página segura do nosso processador de pagamentos (dLocal); os dados do seu cartão não passam por nós. Depois do pagamento, a equipe de reservas confirma a reserva por WhatsApp ou e-mail. Se por algum motivo não for possível confirmar, devolvemos 100%.'¦
EN: 'Payment is made on a secure page of our payment processor (dLocal); your card details do not pass through us. After payment, the reservations team confirms your booking by WhatsApp or email. If for any reason it could not be confirmed, we refund 100%.'¦

ES: 'Te respondemos por WhatsApp o email a la brevedad. El precio y la política que ves acá son los de tu solicitud.'¦
PT: 'Respondemos por WhatsApp ou e-mail o quanto antes. O preço e a política que você vê aqui são os da sua solicitação.'¦
EN: 'We will reply by WhatsApp or email shortly. The price and policy you see here are those of your request.'¦

ES: 'Escribí tu nombre y apellido.'¦
PT: 'Escreva seu nome e sobrenome.'¦
EN: 'Enter your full name.'¦

ES: 'Revisá el email.'¦
PT: 'Confira o e-mail.'¦
EN: 'Check your email.'¦

ES: 'Revisá el teléfono (con código de país).'¦
PT: 'Confira o telefone (com código do país).'¦
EN: 'Check your phone number (with country code).'¦

ES: 'Para seguir, aceptá la política de cancelación.'¦
PT: 'Para continuar, aceite a política de cancelamento.'¦
EN: 'To continue, accept the cancellation policy.'¦

ES: 'Para seguir, aceptá las bases y condiciones.'¦
PT: 'Para continuar, aceite as bases e condições.'¦
EN: 'To continue, accept the booking terms and conditions.'¦

ES: 'Para seguir, aceptá las reglas de la casa.'¦
PT: 'Para continuar, aceite as regras da casa.'¦
EN: 'To continue, accept the house rules.'¦

ES: Preparando el pago…¦
PT: Preparando o pagamento…¦
EN: Preparing the payment…¦

ES: 'Enviando…'¦
PT: 'Enviando…'¦
EN: 'Sending…'¦

ES: 'No pudimos iniciar el pago.'¦
PT: 'Não conseguimos iniciar o pagamento.'¦
EN: 'We could not start the payment.'¦

ES: 'No pudimos enviar la solicitud.'¦
PT: 'Não conseguimos enviar a solicitação.'¦
EN: 'We could not send the request.'¦

ES: ' Escribinos por WhatsApp.'¦
PT: ' Escreva para nós pelo WhatsApp.'¦
EN: ' Message us on WhatsApp.'¦

ES: 'No pudimos iniciar el pago. Escribinos por WhatsApp.'¦
PT: 'Não conseguimos iniciar o pagamento. Escreva para nós pelo WhatsApp.'¦
EN: 'We could not start the payment. Message us on WhatsApp.'¦

ES: <b>Abrimos el pago en otra pestaña.</b><br>Completalo ahí; esta página queda abierta por si querés volver a mirar la propiedad. Si no se abrió, <a href="¦
PT: <b>Abrimos o pagamento em outra aba.</b><br>Conclua por lá; esta página fica aberta caso você queira voltar a olhar a propriedade. Se não abriu, <a href="¦
EN: <b>We opened the payment in another tab.</b><br>Complete it there; this page stays open in case you want to look at the property again. If it did not open, <a href="¦

ES: >tocá acá para ir al pago</a>.¦
PT: >toque aqui para ir ao pagamento</a>.¦
EN: >tap here to go to the payment</a>.¦

ES: >Entendido<¦
PT: >Entendido<¦
EN: >Got it<¦

ES: <b>¡Listo! Recibimos tu solicitud.</b><br>Te escribimos por WhatsApp o email a la brevedad para confirmarte la disponibilidad. Si se aprueba, te mandamos el link para pagar y reservar.¦
PT: <b>Pronto! Recebemos a sua solicitação.</b><br>Escrevemos para você por WhatsApp ou e-mail o quanto antes para confirmar a disponibilidade. Se for aprovada, enviamos o link para pagar e reservar.¦
EN: <b>Done! We received your request.</b><br>We will write to you by WhatsApp or email shortly to confirm availability. If it is approved, we will send you the link to pay and book.¦

ES: 'Sin conexión. Probá de nuevo.'¦
PT: 'Sem conexão. Tente de novo.'¦
EN: 'No connection. Please try again.'¦

ES: 'Demasiadas consultas seguidas. Probá en un minuto.'¦
PT: 'Consultas demais seguidas. Tente em um minuto.'¦
EN: 'Too many requests in a row. Try again in a minute.'¦

ES: 'No pudimos calcular el precio en este momento.'¦
PT: 'Não conseguimos calcular o preço neste momento.'¦
EN: 'We could not calculate the price right now.'¦

ES: Esta propiedad ya no está disponible¦
PT: Esta propriedade não está mais disponível¦
EN: This property is no longer available¦

ES: Mirá las demás opciones que tenemos para tu estadía.¦
PT: Veja as outras opções que temos para a sua estadia.¦
EN: Take a look at the other options we have for your stay.¦

ES: >Ver propiedades</a>¦
PT: >Ver propriedades</a>¦
EN: >View properties</a>¦

ES: Ver las demás propiedades¦
PT: Ver as outras propriedades¦
EN: See the other properties¦

ES: No pudimos cargar la propiedad¦
PT: Não conseguimos carregar a propriedade¦
EN: We could not load the property¦

ES: Probá recargar en un momento, o escribinos por <a¦
PT: Tente recarregar em instantes ou fale com a gente pelo <a¦
EN: Try reloading in a moment, or message us on <a¦
'''


def _parse(texto):
    pares = []
    for bloque in texto.strip('\n').split('\n\n'):
        v = {}
        for linea in bloque.split('\n'):
            if not linea.strip():
                continue
            m = re.match(r'^(ES|PT|EN): (.*)¦$', linea, re.S)
            if not m:
                raise ValueError('línea de pares mal formada: %r' % linea[:80])
            v[m.group(1)] = m.group(2).replace('\\n', '\n')
        if 'ES' not in v:
            raise ValueError('bloque sin ES: %r' % bloque[:80])
        pares.append((v['ES'], v.get('PT', v['ES']), v.get('EN', v['ES'])))
    return pares


def _resumen_reglas():
    """Resumen de reglas de la casa: textos oficiales de tools/legales_reserva.py (RESUMEN)."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    try:
        from legales_reserva import RESUMEN
    except Exception:
        return []
    es, pt, en = RESUMEN['es'], RESUMEN['pt'], RESUMEN['en']
    out = [(es['intro'], pt['intro'], en['intro']), (es['cierre'], pt['cierre'], en['cierre'])]
    for a, b, c in zip(es['items'], pt['items'], en['items']):
        out.append((a, b, c))
    return out


PARES = _parse(_DATOS) + _parse(_DATOS_FICHA) + _resumen_reglas()

# Si un mismo es aparece repetido con la misma traducción, se deja uno; con traducciones distintas es un error.
def _unicos(pares):
    vistos, out = {}, []
    for es, pt, en in pares:
        if es in vistos:
            if vistos[es] != (pt, en):
                raise ValueError('par duplicado con traducciones distintas: %r' % es[:80])
            continue
        vistos[es] = (pt, en)
        out.append((es, pt, en))
    return out

PARES = _unicos(PARES)

# ── Documentos legales por idioma (la ficha los lee de las páginas del sitio) ───────────────────────────────────
DOCS_URL = {
    'pt': {'bases': '/pt/condicoes-reserva.html', 'reglas': '/pt/regras-da-casa.html'},
    'en': {'bases': '/en/booking-terms.html', 'reglas': '/en/house-rules.html'},
    'es': {'bases': '/condiciones-reserva.html', 'reglas': '/reglas-de-la-casa.html'},
}

_RX = {}
_MAP = {}
def _compilar(lang):
    if lang in _RX:
        return
    i = 1 if lang == 'pt' else 2
    mapa = {}
    for par in PARES:
        mapa[par[0]] = par[i]
    claves = sorted(mapa, key=len, reverse=True)
    _MAP[lang] = mapa
    _RX[lang] = re.compile('|'.join(re.escape(k) for k in claves))


def traducir(src, lang, uso=None):
    """Aplica los pares (una sola pasada, la alternativa más larga primero). lang: 'es' (igual), 'pt' o 'en'.
    `uso` (dict opcional): se llena con {es: cantidad_de_reemplazos} para auditar qué pares se aplicaron."""
    if lang == 'es':
        return src
    if lang not in ('pt', 'en'):
        raise ValueError('idioma no soportado: %s' % lang)
    _compilar(lang)
    mapa = _MAP[lang]
    def f(m):
        if uso is not None:
            uso[m.group(0)] = uso.get(m.group(0), 0) + 1
        return mapa[m.group(0)]
    return _RX[lang].sub(f, src)


# ── Textos del armado de fichas (tools/generar-fichas.py): descripción corta, propiedad retirada ──────────────
TIPO = {'es': ('Casa', 'Apartamento'), 'pt': ('Casa', 'Apartamento'), 'en': ('House', 'Apartment')}
def descripcion_ficha(lang, tipo, barrio, dormitorios=None, huespedes=None):
    """Descripción corta (meta description / og / JSON-LD) en el idioma pedido."""
    t = TIPO[lang][0 if tipo == 'casa' else 1]
    if lang == 'pt':
        partes = ['%s em %s' % (t, barrio)]
        if dormitorios: partes.append('%s dormitório%s' % (dormitorios, '' if str(dormitorios) == '1' else 's'))
        if huespedes: partes.append('até %s hóspedes' % huespedes)
        return ', '.join(partes) + '. Reserve direto com a Premium Host Punta: disponibilidade e preço real na hora.'
    if lang == 'en':
        partes = ['%s in %s' % (t, barrio)]
        if dormitorios: partes.append('%s bedroom%s' % (dormitorios, '' if str(dormitorios) == '1' else 's'))
        if huespedes: partes.append('up to %s guests' % huespedes)
        return ', '.join(partes) + '. Book direct with Premium Host Punta: real availability and price instantly.'
    partes = ['%s en %s' % (t, barrio)]
    if dormitorios: partes.append('%s dormitorios' % dormitorios)
    if huespedes: partes.append('hasta %s huéspedes' % huespedes)
    return ', '.join(partes) + '. Reservá directo con Premium Host Punta: disponibilidad y precio real al instante.'

RETIRADA = {'es': ('Propiedad no disponible', 'Esta propiedad ya no está disponible.'),
            'pt': ('Propriedade indisponível', 'Esta propriedade não está mais disponível.'),
            'en': ('Property unavailable', 'This property is no longer available.')}


# ── restos(): lo que quedó en español y se VE ───────────────────────────────────────────────────────────────────
_ES_PALABRAS = set("""el los las una unos unas tu tus su sus hay está están más también cuando sin con por desde hasta
propiedad propiedades noche noches huésped huéspedes llegada salida reserva reservar reservas estadía elegí elegir escribinos
consultá consultanos probá mové mirá hacé tenés podés querés buscás disponible disponibles incluye incluida fechas fecha
precio precios aceptá aceptar cancelación política garantía saldo seña limpieza piscina playa cerca zona zonas mapa lista
ver mostrar mostrando todas todos para quien nuestra nuestras nuestro nuestros esta este esos esas ese esa donde dónde cómo
qué cuál cuándo quiénes ahora todavía acá allí ahí algún alguna algo nada siempre además según después antes durante entre
sobre pero porque aunque mientras dormitorios dormitorio baños baño comodidades reglas casa casas apartamento apartamentos
usuario contraseña entrar salir cerrar volver cancelar enviar solicitud nombre apellido teléfono mensaje equipo opcional
filtros limpiar buscar adultos niños bebés recomendadas menor mayor cualquiera frente mar calendario calendarios
leí acepto bases condiciones ya no solo tiempo real del al un y o de la lo le se es son como mas muy mes dia dias hora""".split())
# palabras que SÍ son válidas en portugués / inglés aunque estén en la lista del español
_PT_OK = set("""a e o os as de da do em no na um uma com para por que se ao à às ou mais mas muito não ver mapa lista local total
casa casas nome sobre antes depois entre desde até ate piscina zona zonas reserva reservar reservas hóspede hóspedes estadia saldo
mensagem telefone mês dia dias hora horas frente mar política mostrar mostrando todas todos esta este esse essa esses essas
cancelar enviar entrar sair voltar buscar filtros limpar adultos menor maior opcional equipe usuário nome algo nada sempre
apartamento apartamentos comodidades la está estão como ainda durante quem nossa nosso donde cálculo bases condições é são mês tempo real sem solo""".split())
_EN_OK = set("""no real solo mar total local area plan a an on in me us it is to the of or one for by up and as at be he if so we do go
my am are not map can all any yes mes con una""".split())

_RX_CAR = re.compile(r'[ñ¿¡]|ción\b|ciones\b|sión\b')
_RX_PALABRA = re.compile(r"[^\W\d_]+", re.U)
_RX_COMENT_JS = re.compile(r'(?m)^\s*//.*$|(?<=[\s;,)])//[^\n]*$')
_RX_COMENT_HTML = re.compile(r'<!--.*?-->', re.S)
_RX_COMENT_BLOQ = re.compile(r'/\*.*?\*/', re.S)
_ALLOW = ('Punta del Este', 'Premium Host Punta', 'PHPunta', 'La Barra', 'Manantiales', 'José Ignacio', 'Punta Ballena',
          'Playa Mansa', 'Playa Brava', 'Laguna del Sauce', 'Beverly Hills', 'San Rafael', 'Roosevelt', 'Montevideo',
          'Península', 'Peninsula', 'Felipe Zerbino', 'MINTUR', 'Registro MINTUR', 'Playa')


def _sospechoso(t, lang):
    t0 = t
    for a in _ALLOW:
        t0 = t0.replace(a, ' ')
    if _RX_CAR.search(t0):
        return True
    pal = [w.lower() for w in _RX_PALABRA.findall(t0)]
    if lang == 'en':
        if re.search(r'[áéíóúüãõç]', t0, re.I):
            return True
        return any(w in _ES_PALABRAS and w not in _EN_OK for w in pal)
    return any(w in _ES_PALABRAS and w not in _PT_OK for w in pal)


def _candidatos(src):
    """Textos visibles candidatos: nodos de texto del HTML, atributos visibles y literales de JS (sin comentarios, console.log)."""
    s = _RX_COMENT_HTML.sub(' ', src)
    out = []
    # <style> fuera
    s = re.sub(r'<style\b.*?</style>', ' ', s, flags=re.S)
    # scripts
    def script(m):
        cuerpo = m.group(1)
        cuerpo = _RX_COMENT_BLOQ.sub(' ', cuerpo)
        cuerpo = _RX_COMENT_JS.sub('', cuerpo)
        cuerpo = re.sub(r'console\.(log|warn|error)\([^;\n]*\);?', ' ', cuerpo)
        for lit in re.finditer(r"'((?:[^'\\\n]|\\.)*)'|\"((?:[^\"\\\n]|\\.)*)\"", cuerpo):
            t = lit.group(1) if lit.group(1) is not None else lit.group(2)
            # texto dentro de literal que contiene HTML: tomar los nodos de texto y atributos
            out.append(t)
        return ' '
    s = re.sub(r'<script\b[^>]*>(.*?)</script>', script, s, flags=re.S)
    # atributos visibles
    for m in re.finditer(r'\b(?:placeholder|aria-label|title|alt|content)="([^"]*)"', s):
        out.append(m.group(1))
    # nodos de texto
    for m in re.finditer(r'>([^<>]+)<', s):
        out.append(m.group(1))
    return out


def restos(src_traducido, lang='pt'):
    """Lista de textos que parecen seguir en español (heurística). Ignora comentarios, console.log, CSS e identificadores.
    Un texto es candidato si lo ve el usuario (nodo de texto, atributo placeholder/aria-label/title/alt/content o literal de JS)."""
    res, vistos = [], set()
    for t in _candidatos(src_traducido):
        t = t.strip()
        if len(t) < 3 or not re.search(r'[A-Za-zÁÉÍÓÚáéíóúñ]{3}', t):
            continue
        # identificadores / selectores / rutas / urls / claves
        if re.match(r'^[#.\[\]a-zA-Z0-9_\-:/=?&%@.,*()| ]+$', t) and ' ' not in t.strip() :
            continue
        if re.match(r'^(https?:|/|#|\.|\{|<svg|translate|rgba?|var\(|M\d)', t):
            continue
        texto = re.sub(r'<[^>]+>', ' ', t)         # lo de adentro de un literal con HTML
        texto = re.sub(r'<[^>]*$', ' ', texto); texto = re.sub(r'^[^<>]*">', ' ', texto)
        texto = re.sub(r'&[a-z#0-9]+;', ' ', texto)
        # selectores CSS / claves de objeto / nombres de evento sueltos
        if re.match(r'^[#.\[][\w\-\[\]="\'.# >:]*$', texto.strip()):
            continue
        if _sospechoso(texto, lang) and texto.strip() not in vistos:
            vistos.add(texto.strip())
            res.append(texto.strip())
    return res


if __name__ == '__main__':
    print('pares:', len(PARES))

# Sistema visual ZeloKids — imagens de produto

Referência aprovada pelo dono: `trava-macaneta/` (piloto de 19/10/2026).

## Formato
- 1024 × 1024 px, JPG qualidade 90.
- Nome do arquivo: `<palavra-chave-principal>-NN-<funcao>.jpg`, minúsculas, sem acento, hífens.
  Funções: 01-capa, 02-em-uso, 03-problema, 04-beneficio, 05-como-funciona, 06-diferenciais, 07-duvidas, 08-onde-usar, 09-resumo.

## Cores e letra
- Roxo **#5C54E9** em todo texto (título, apoio, itens) e nos círculos de ícone.
- Verde **#BAE150** em detalhes pequenos, nunca em texto: traço curto abaixo do título, borda dos números e marcadores, checks, ícones dos chips, check do escudo.
- Branco #FFFFFF de fundo.
- Tipografia da marca: **Capriola** na linha forte do título; **Rubik** na linha leve do título (300), no apoio (400) e nos itens (600/400).
- Não usar: títulos marrom, cinza, salmão ou coral; corações; rabiscos; círculos multicoloridos; rodapé ondulado; emoji; personagens; logotipo ou nome "ZeloKids" na arte (só se o dono pedir).

## A galeria (9 imagens, nesta ordem)
| # | Tipo | Layout | Conteúdo |
|---|---|---|---|
| 01 | Capa | `capa` | Só o produto, fundo 100% branco, sem texto e sem ícone (Google Shopping/PMax recusa texto na foto principal) |
| 02 | Produto em uso | `hero` | Cenário real de casa + título com o nome do produto + apoio curto + escudo |
| 03 | Dor / problema | `card` | Situação que o produto resolve (sem criança em risco) + pergunta da dor |
| 04 | Benefício principal | `card` | Resultado/transformação + escudo |
| 05 | Como funciona | `lista` num | Até 3 passos numerados |
| 06 | Diferenciais | `lista` ícones | Até 3 diferenciais reais |
| 07 | Quebra de objeções | `lista` ícones | Compatibilidade, medidas, material |
| 08 | Praticidade | `card` + chips | Onde usar (até 3 chips) |
| 09 | Resumo | `lista` checks | Até 4 motivos |

## Estudo do produto (antes de qualquer arte)
- Juntar TODAS as fotos: galeria atual da loja (página do produto, imagens `acdn-us.mitiendanube.com/.../products/...-1024-1024.webp`), fotos do fornecedor (pasta `D:\Downloads\<nome>_<id>_images` ou o que o resumo do agente SEO indicar) e o `resumo-fornecedor.md`.
- Escrever `ficha-visual.md`: partes obrigatórias (botões, ícones, parafusos, texturas, setas), vistas disponíveis, melhor referência de estúdio, ideias de destaque com origem, o que não afirmar.
- A referência para o Gemini é sempre a foto mais nítida e completa (de preferência a de estúdio da loja), nunca uma miniatura.

## Destaque de partes (diferenciais)
- Marcadores numerados (círculo roxo, borda verde) AO LADO da parte, sem cobri-la, ligados à lista numerada. Nada de linhas puxadas.

## Regras de conteúdo
- Toda afirmação vem da página do produto na Nuvemshop, do resumo do agente SEO ou de avaliação de cliente. Nada inventado.
- Se faltar dado para uma imagem (ex.: medidas), ela é pulada — nunca preenchida com chute.
- Apoio no máximo 2 linhas; itens com título curto + descrição de 1 linha.

## Fotos e cenários (Gemini)
- O produto na imagem final é **exatamente** o da foto original: forma, cor, proporção, texturas, setas, logos.
- Capa: pedir ao Gemini só a troca do fundo por branco puro; o renderizador força o branco e corta a margem.
- Cenário com espaço para título (`hero`): usar `--pad 0.62` (produto reduzido no centro-baixo). Funciona quando o fundo é liso (parede/porta).
- Se o Gemini deixar emenda/faixa (comum em fundo complexo), usar o layout `card` recortando a parte boa da cena.
- Máximo 2 tentativas por imagem; depois disso, usar foto original com fundo limpo.
- Prompt sempre em inglês, terminando com: sem texto, sem logos, sem pessoas/mãos (salvo cena de uso pedida), foto realista.
- Bebê/criança, quando aparecer: sempre vestido, cena de produto/estilo de vida, nunca em situação de risco.

## Alt text
- Descreve o que aparece + palavra-chave (ou variação) da página. Até ~125 caracteres. Um diferente por imagem.

## Conferência antes de publicar
Reprovar e refazer se: produto alterado; texto com erro; título fora do roxo; mais de um tratamento de título; ícone multicolorido; corte no produto; emenda visível no cenário; formato diferente de 1024.

## Ferramentas do kit (resumo)
- `render.py <spec> --out-dir <pasta> [--only 01,06]` — gera as artes; `--only` re-renderiza só algumas; sempre grava `_preview.jpg` (folha 3x3) e imprime AVISO quando a capa não está branca nos cantos, o alt falta ou passa de 140 caracteres.
- `publicar.py <spec> [--sha <commit>]` — imprime o payload `images` pronto para o `update_product` (URL fixa no commit, posições 1..N, alt pt_BR).
- `gerar_cena.py --ref foto --prompt txt --out png [--pad 0.6]` — Gemini; roda no computador do dono (chave no .env).

## Exceções de capa
- Produto grande ou "de cena" (rede de proteção, tatame, mosquiteiro): se não der para isolar em branco sem distorcer, a capa é a melhor foto limpa do produto em fundo neutro claro, ainda sem texto e sem ícone.
- Kits (ex.: 20 protetores de tomada): a capa mostra o conteúdo do kit arrumado, não uma peça só.
- Variantes de cor: uma foto por cor entra na galeria (depois das 9) e o dono associa à variante no admin; o conector não faz essa associação.

## Títulos
- Cada linha do título cabe em ~930 px: até ~20 caracteres na linha forte (Capriola) e ~24 na leve. O renderizador reduz a fonte se passar, mas acima disso o título fica pequeno — reescreva em vez de depender da redução.

## Limpeza de fundo (aprendido no protetor de cabeça, 19/10/2026)
- Nunca clarear por limiar global ("tudo acima de X vira branco"): produtos creme/bege/branco perdem pedaços. Separar o fundo pela cor dele (neutro, pouco saturado) ligado às bordas, manter só as regiões grandes do produto e suavizar 1 px.
- Depois do recorte, aplicar máscara de nitidez leve (UnsharpMask raio 1,5 / 65%): o Gemini flash entrega a foto um pouco macia.
- Para mais qualidade na capa/close: `gerar_cena.py --model gemini-3.1-pro-image --size 2K` (custa mais; usar só na capa e no close de detalhe) ou partir da foto de estúdio da loja quando ela já for nítida.

## Fotos existentes também passam por melhoria (regra do dono, 19/10/2026)
- Toda foto da loja ou do fornecedor que entrar numa arte (recortada ou ampliada) passa ANTES pelo Gemini pro em 2K com o prompt de melhoria (`prompts/melhorar.txt`: upscale + nitidez, tudo idêntico), depois reduz para 1024 com Lanczos + UnsharpMask leve. Sem isso a foto ampliada fica macia e destoa das geradas.
- Conferir a melhoria como qualquer geração (o pro pode trocar textura ou reenquadrar). Em paralelo, os arquivos de saída podem vir trocados entre si: identifique pelo conteúdo, não pelo nome.
- Modelo padrão: `gemini-3-pro-image --size 2K` para capa, cenários e melhoria; o flash só para testes.

## v2 — nitidez, zoom e variedade de layout (pedido do dono, 19/10/2026)
- **Render em 2K**: o `render.py` monta a arte em 2048 px (fontes de `_fontes/pro-2k/` quando existem) e reduz para 1024 com Lanczos + nitidez leve. Nunca montar em 1024 direto.
- **Cena de uso nasce no Gemini**: não esticar/outpaint foto antiga da loja (vem macia); gerar a cena do zero com a foto de estúdio limpa como `--ref` e conferir o produto.
- **Diferenciais com lupa** (layout `detalhe`): cada parte tem uma lupa circular (borda verde) com o zoom real da foto, o número preso na lupa e uma linha fina roxa até o ponto da peça. Substitui os marcadores soltos.
- **Variar o layout**: nunca repetir o mesmo arranjo em imagens seguidas. Sugestão padrão: 02 `hero` · 03 `split` · 04 `overlay` · 05 `lista` (side right) · 06 `detalhe` · 07 `lista` · 08 `card`+chips · 09 `passos`.

## v3 — galeria maior e identidade por produto (decisões do dono, 20/10/2026)
- **Galeria = capa + 12 narrativas + variantes.** Posição 1: capa, só produto em fundo 100% branco. Posições 2–13: 12 imagens narrativas (9 papéis fixos — em uso, problema, benefício, como funciona, diferenciais com lupas, dúvidas/medidas, onde usar, resumo, segunda cena de uso — + 3 vagas livres do criativo). Posição 14 em diante: uma foto em branco por variante confirmada, para o dono associar no admin. O dono publica tudo e poda o que não quiser.
- Capa e variantes: produto nítido, fundo #FFFFFF, sem texto, ícone ou selo. Variante gerada em branco a partir da foto colorida é conferida contra a foto do fornecedor.
- Segunda camada: a skill `criativo-zelokids` define, produto a produto, as 12 narrativas: identidade em 1 frase, gancho, protagonista/cenário/luz, cena e layout de cada imagem (diferenciais sempre com lupas). Entrega `briefing-criativo.md` + `spec.json` revisado; o diretor de arte gera e publica.
- Nas 12 narrativas: no mínimo 9 layouts diferentes, no máximo 2 repetidos e nunca vizinhos; produtos vizinhos não repetem a mesma sequência.
- Layouts novos no `render.py` (campos no cabeçalho do arquivo): `comparativo` (img + img2, chips Sem/Com) · `depoimento` (quote literal de cliente + 5 estrelas verdes; sem nome) · `numero` (num gigante + legend) · `sequencia` (steps 1-2-3 com foto cada) · `faixa` (foto sangrada + faixa branca sólida em cima ou embaixo) · `mosaico` (1 grande + 2 pequenas com label) · `pergunta` (q em Capriola grande, `\n` quebra linha; a = resposta) · `cheia` (só foto + chip).
- Primeiro produto no v3: mosquiteiro de carrinho (pai, fim de tarde, vista de dentro do tule).

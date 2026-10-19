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

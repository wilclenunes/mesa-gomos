# Configurador de Gomos — contexto do projeto

## O que é
Simulador 3D para a web de uma mesa de cabeceira redonda desenhada por Wilcle Nunes para a Bocote
(marca de mobiliário e design da Apoio à Casa — não descrever como "fábrica").

A mesa tem 3 gavetas cilíndricas. Cada gaveta é revestida por 24 gomos estofados (bouclé), 72 no total.
A ideia de produto: os gomos encaixam e desencaixam (tipo lego), e o cliente escolhe o tecido de cada um.
A mesa é entregue montada numa caixa; os gomos são o diferencial e podem vender-se em packs à parte.

## Quem trabalha nisto
Wilcle é arquiteto e iniciante em programação. Explica sempre em português de Portugal, em passos simples,
e diz o que mudaste e porquê antes de entrar em detalhe técnico.

## Estado atual
- `index.html` é um ficheiro único: HTML + CSS + JavaScript, sem build.
- 3D com three.js r128 (carregado de CDN) + OrbitControls.
- Gomo = geometria "almofada" gerada por código (função `ribGeometry`), repetida 24x por gaveta.
- Textura bouclé gerada num `<canvas>` (sem imagens externas).
- Toque num gomo pinta-o; modo "Gaveta inteira" pinta a gaveta; composições rápidas; cor dos aros.
- Lista de gomos necessários por tecido. Configuração guardada no `localStorage` do navegador.

## Medidas usadas no modelo (metros, aproximadas)
Diâmetro 0,50 · altura de cada gaveta 0,152 · aro entre gavetas 0,02 · base 0,034 · espessura do gomo 0,024.
Se o Wilcle der medidas reais, substitui as constantes `R, T, H, GAP, BASE` em `init3D()`.

## Próximos passos possíveis (por ordem sugerida)
1. Medidas reais e número real de gomos por gaveta.
2. Tecidos reais: fotografias/amostras do fornecedor como texturas (pasta `textures/`).
3. Animação de "tirar e pôr" um gomo, para mostrar o encaixe.
4. Abrir gavetas com um toque.
5. Botão "Pedir orçamento" que envia a configuração (código curto ou link).
6. Passar para Vite + React Three Fiber só se o projeto crescer; até lá, manter ficheiro único.

## Regras
- Mantém tudo a funcionar abrindo `index.html` diretamente no navegador.
- Testa no telemóvel (largura ~400px).
- Não inventes preços nem referências de tecido; pergunta ao Wilcle.

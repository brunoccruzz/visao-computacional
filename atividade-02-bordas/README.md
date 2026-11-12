# Atividade 02 — Detecção de bordas e contagem de objetos

Aplica o pipeline visto em aula para encontrar e contar objetos numa imagem:

1. Conversão para **tons de cinza**
2. **Blur** para tirar ruído
3. **Binarização** com o método de Otsu (`mahotas`)
4. Detector de bordas **Canny**
5. **Contornos externos** (`cv2.RETR_EXTERNAL`) → quantidade de objetos

## Uso

```bash
python bordas.py foto.jpg                         # padrão: blur 7, canny 70/150
python bordas.py foto.jpg --blur 11 --canny 30 100
python bordas.py --camera --nome selfie           # tira a foto pela webcam (ESPAÇO / ESC)
python bordas.py foto.jpg --comparar              # gera as grades de comparação
python bordas.py foto.jpg --comparar --sem-janela # só salva, sem abrir janelas
```

Saídas em `saida/` (ignorada pelo git):

| Arquivo | Conteúdo |
|---|---|
| `<nome>_etapas_*.jpg` | cinza, blur, binarização e Canny lado a lado |
| `<nome>_resultado_*.jpg` | contornos desenhados na foto + contagem |
| `<nome>_comparacao.jpg` | grade 3×3: blur (3, 7, 15) × Canny (30/100, 70/150, 150/250) |
| `<nome>_canny_sem_binarizar.jpg` | mesma grade, com o Canny aplicado direto na imagem suavizada |

## Observação sobre os parâmetros

No pipeline da aula o Canny recebe a imagem **já binarizada**: só existem pixels 0 e 255,
então todo degrau tem gradiente máximo e passa em qualquer limiar. Por isso mudar os
limiares do Canny não altera a contagem. Quem muda o resultado é o **blur**, porque ele age
antes do Otsu e muda o formato das regiões brancas/pretas.

A grade `canny_sem_binarizar` mostra o efeito real dos limiares: limiares baixos pegam
mais bordas (incluindo ruído e reflexos), limiares altos ficam só com as bordas fortes.

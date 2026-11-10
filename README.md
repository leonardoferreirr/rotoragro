# Rotor Agro: site

Site estático de manutenção de drones agrícolas e baterias. Tudo sai do `build.py`.

```
python3 tools/preparar.py   # fontes e imagens a partir da marca (só quando a marca mudar)
python3 build.py            # gera as páginas, sitemap, robots e llms.txt
node tools/servir.mjs 4230  # servidor local com gzip e URLs limpas
```

## Antes de ligar o Google (`INDEXAR = True` no build.py)

- `WHATSAPP` e `TEL_VER`: número real.
- `CIDADE`: cidade e estado da oficina. Com ela, o rodapé, o schema e o llms.txt passam a citar a região.
- Confirmar com o cliente o que o site afirma:
  - que atende qualquer revenda;
  - a lista de `MODELOS`;
  - que o orçamento sai antes do conserto;
  - o teste de bateria com etiqueta;
  - a entrega com selo e ordem de serviço;
  - a retirada na região.
- Registrar rotoragro.com.br e apontar para a Vercel. O canônico já é `www.rotoragro.com.br`.

## Estrutura

- `_src/site.css` e `_src/site.js`: estilo e comportamento. O build copia o JS para `assets/js/`.
- `tools/drone.py`: o drone da abertura, com braços que abrem no scroll e o O da marca como hélice.
- Ícones lidos de `06_OUTPUTS/rotor-agro/marca/icones` no kit.

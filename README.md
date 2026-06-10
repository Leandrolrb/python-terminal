# Python Terminal

Um terminal/shell interativo construído em Python para executar comandos do sistema.

## Funcionalidades

- Interface interativa com prompt mostrando diretório atual
- Execução de comandos do sistema via `subprocess`
- Navegação de diretórios com `cd`
- Histórico de comandos em memória durante a sessão
- Comandos built-in:
  - `cd`
  - `pwd`
  - `help`
  - `clear`
  - `exit` / `quit`
- Suporte básico a pipes e redirecionamentos (`|`, `>`, `<`)
- Tratamento de erros para comandos inválidos

## Estrutura

- `/home/runner/work/python-terminal/python-terminal/Leandrolrb/python-terminal/main.py`
- `/home/runner/work/python-terminal/python-terminal/Leandrolrb/python-terminal/terminal.py`
- `/home/runner/work/python-terminal/python-terminal/Leandrolrb/python-terminal/commands.py`
- `/home/runner/work/python-terminal/python-terminal/Leandrolrb/python-terminal/requirements.txt`

## Instalação

```bash
python -m pip install -r requirements.txt
```

## Uso

```bash
python main.py
```

Exemplos no terminal:

```bash
/home/user/project $ pwd
/home/user/project

/home/user/project $ cd ..
/home/user $

/home/user $ echo "olá" | tr a-z A-Z
OLÁ

/home/user $ echo "texto" > saida.txt
/home/user $ cat < saida.txt
texto

/home/user $ help
```

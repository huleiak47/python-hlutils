set nocompatible
filetype off
set number
set numberwidth=3
set noerrorbells
set vb t_vb=

set wrap
set textwidth=80
set noswapfile
set ignorecase
set smartcase
set incsearch
set hlsearch
set expandtab
set fencs=ucs-bom,utf-8,gbk,big5,latin-1
set encoding=gbk
set fileformats=dos,unix

python << PYEOF
import vim
import os

def write_line():
    line = vim.eval("getline('.')")
    fname = vim.eval("expand('%:p')")
    fname = os.path.splitext(fname)[0] + ".sel"
    with open(fname, "wb") as f:
        f.write(line.strip())

PYEOF

nmap <CR> :python write_line()<CR>:q!<CR>
nmap <ESC> :q!<CR>

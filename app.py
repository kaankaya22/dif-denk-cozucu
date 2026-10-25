import numpy as np 
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import ast
import time
#Euler
def euler(f, x0, y0, h, n):
    x = np.zeros(n + 1)
    y = np.zeros(n + 1)

    x[0] = x0
    y[0] = y0

    for i in range(n):
        x[i + 1] = x[i] + h
        y[i + 1] = y[i] + h * f(x[i], y[i])

    return x, y
def heun(f, x0, y0, h, n):
    x = np.zeros(n + 1)
    y = np.zeros(n + 1)

    x[0] = x0
    y[0] = y0

    for i in range(n):
        x[i + 1] = x[i] + h

        # Tahmin
        k1 = f(x[i], y[i])
        y_tahmin = y[i] + h * k1

        # Duzeltme
        k2 = f(x[i + 1], y_tahmin)

        y[i + 1] = y[i] + (h / 2) * (k1 + k2)

    return x, y
def rk4(f, x0, y0, h, n):
    x = np.zeros(n + 1)
    y = np.zeros(n + 1)

    x[0] = x0
    y[0] = y0

    for i in range(n):
        k1 = f(x[i], y[i])

        k2 = f(x[i] + h/2,
               y[i] + h*k1/2)

        k3 = f(x[i] + h/2,
               y[i] + h*k2/2)

        k4 = f(x[i] + h,
               y[i] + h*k3)

        y[i + 1] = y[i] + (h/6)*(k1 + 2*k2 + 2*k3 + k4)
        x[i + 1] = x[i] + h

    return x, y
st.set_page_config(
    page_title="Diferansiyel Denklem Cozucu",
    layout="wide"
)
st.title("Diferansiyel Denklem Çözücü")
st.write("1. dereceden diferansiyel denklemlerin sayısal çözümü")

# DENKLEM OKUMA FONKSIYONU
def denklem_olustur(metin):
    izinli_fonksiyonlar = {
        "sin": np.sin,
        "cos": np.cos,
        "tan": np.tan,
        "exp": np.exp,
        "sqrt": np.sqrt,
        "log": np.log,
        "abs": np.abs
    }

    izinli_islemler = (
        ast.Expression, ast.BinOp, ast.UnaryOp,
        ast.Add, ast.Sub, ast.Mult, ast.Div,
        ast.Pow, ast.UAdd, ast.USub,
        ast.Constant, ast.Name, ast.Load,
        ast.Call
    )

    agac = ast.parse(metin, mode="eval")

    for dugum in ast.walk(agac):
        if not isinstance(dugum, izinli_islemler):
            raise ValueError("İzin verilmeyen matematiksel ifade")

        if isinstance(dugum, ast.Name):
            if dugum.id not in ("x", "y", *izinli_fonksiyonlar):
                raise ValueError("Bilinmeyen değişken veya fonksiyon")

        if isinstance(dugum, ast.Call):
            if (not isinstance(dugum.func, ast.Name)
                    or dugum.func.id not in izinli_fonksiyonlar
                    or len(dugum.args) != 1
                    or dugum.keywords):
                raise ValueError("Geçersiz fonksiyon kullanımı")

    kod = compile(agac, "<denklem>", "eval")

    def f(x, y):
        ortam = {"x": x, "y": y, **izinli_fonksiyonlar}
        return eval(kod, {"__builtins__": {}}, ortam)

    return f

# KULLANICI GIRISLERI
st.sidebar.header("Parametreler")

denklem = st.sidebar.text_input(
    "dy/dx = f(x,y)",
    value="x + y"
)

yontem = st.sidebar.selectbox(
    "Sayısal yöntem",
    ["Euler", "Heun", "RK4"]
)

x0 = st.sidebar.number_input(
    "Başlangıç x0", value=0.0
)

y0 = st.sidebar.number_input(
    "Başlangıç y0", value=1.0
)

h = st.sidebar.number_input(
    "Adım büyüklüğü h",
    min_value=0.0001,
    value=0.1,
    format="%.4f"
)

n = st.sidebar.number_input(
    "Adım sayısı",
    min_value=1,
    max_value=10000,
    value=20,
    step=1
)

coz = st.sidebar.button("Denklemi Çöz")

# SAYISAL COZUM
if coz:
    try:
        f = denklem_olustur(denklem)

        if yontem == "Euler":
            x, y = euler(f, x0, y0, h, n)

        elif yontem == "Heun":
            x, y = heun(f, x0, y0, h, n)

        else:
            x, y = rk4(f, x0, y0, h, n)

        if not np.all(np.isfinite(y)):
            raise ValueError("Çözümde tanımsız veya sonsuz değer oluştu")

        st.success("Denklem başarıyla çözüldü!")
# GRAFIK
       

        # CANLI GRAFIK
        grafik_alani = st.empty()

        plt.figure(figsize=(10, 6))

        y_min = min(y)
        y_max = max(y)
        bosluk = max((y_max - y_min) * 0.1, 0.1)

        for i in range(1, len(x) + 1):

            plt.clf()

            plt.plot(x[:i], y[:i], "o-", label=yontem)

            plt.xlim(min(x), max(x))
            plt.ylim(y_min - bosluk, y_max + bosluk)

            plt.xlabel("x")
            plt.ylabel("y")
            plt.title("Canlı Sayısal Çözüm")
            plt.legend()
            plt.grid()

            grafik_alani.pyplot(plt.gcf())

            time.sleep(0.05)

        plt.close()



        # SONUC TABLOSU
        tablo = pd.DataFrame({
            "x": x,
            "y": y
        })

        st.subheader("Sayısal Sonuçlar")
        st.dataframe(tablo)

        st.write("Son noktadaki sonuç:", y[-1])

    except Exception as hata:
        st.error(f"Hata oluştu: {hata}")
           

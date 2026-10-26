#!/usr/bin/env python3
"""
Tugas 6 - Node B (penerima pesan) menggunakan Reticulum Network Stack (RNS).

Node B:
  1. Menjalankan instance Reticulum dengan konfigurasi di ./config_node_b
  2. Memuat (atau membuat) Identity -> pasangan kunci X25519 + Ed25519
  3. Membuat Destination IN/SINGLE "tugas6.pesan"
  4. Meng-announce destination tersebut ke jaringan
  5. Menampilkan setiap pesan yang diterima dari Node A

Jalankan:  python3 node_b.py
"""

import os
import sys
import time

import RNS

APP_NAME = "tugas6"
ASPECT   = "pesan"

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR    = os.path.join(BASE_DIR, "config_node_b")
IDENTITY_PATH = os.path.join(CONFIG_DIR, "identity_node_b")


def load_or_create_identity():
    # Identity disimpan ke file agar hash destination Node B tetap sama
    # setiap kali program dijalankan ulang.
    if os.path.isfile(IDENTITY_PATH):
        identity = RNS.Identity.from_file(IDENTITY_PATH)
        print("[Node B] Identity dimuat dari file")
    else:
        identity = RNS.Identity()
        identity.to_file(IDENTITY_PATH)
        print("[Node B] Identity baru dibuat dan disimpan")
    return identity


def packet_received(data, packet):
    pesan = data.decode("utf-8")
    waktu = time.strftime("%H:%M:%S")
    print(f"[Node B] {waktu} Pesan diterima dari Node A : \"{pesan}\"")
    sys.stdout.flush()


def main():
    RNS.Reticulum(configdir=CONFIG_DIR)

    identity = load_or_create_identity()

    destination = RNS.Destination(
        identity,
        RNS.Destination.IN,
        RNS.Destination.SINGLE,
        APP_NAME,
        ASPECT,
    )
    # Kirim bukti penerimaan (proof) otomatis untuk setiap paket
    destination.set_proof_strategy(RNS.Destination.PROVE_ALL)
    destination.set_packet_callback(packet_received)

    print(f"[Node B] Identity hash    : {RNS.prettyhexrep(identity.hash)}")
    print(f"[Node B] Destination name : {destination.name}")
    print(f"[Node B] Destination hash : {RNS.prettyhexrep(destination.hash)}")
    print(f"[Node B] Jalankan Node A dengan:")
    print(f"         python3 node_a.py {destination.hexhash} \"isi pesan\"")
    print("[Node B] Menunggu pesan... (Ctrl+C untuk berhenti)")
    sys.stdout.flush()

    # Announce secara berkala agar Node A dapat menemukan path & public key
    try:
        while True:
            destination.announce()
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n[Node B] Berhenti")


if __name__ == "__main__":
    main()

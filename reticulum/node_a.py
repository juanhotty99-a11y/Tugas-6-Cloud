#!/usr/bin/env python3
"""
Tugas 6 - Node A (pengirim pesan) menggunakan Reticulum Network Stack (RNS).

Node A:
  1. Menjalankan instance Reticulum dengan konfigurasi di ./config_node_a
  2. Mencari path ke destination hash milik Node B (request_path)
  3. Mengambil public key Node B dari announce (Identity.recall)
  4. Membuat Destination OUT/SINGLE "tugas6.pesan" milik Node B
  5. Mengirim pesan terenkripsi ke Node B dan menunggu bukti penerimaan

Jalankan:  python3 node_a.py <destination_hash_node_b> ["isi pesan"]
Jika isi pesan tidak diberikan, program masuk ke mode interaktif.
"""

import os
import sys
import time

import RNS

APP_NAME = "tugas6"
ASPECT   = "pesan"

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, "config_node_a")

PATH_TIMEOUT  = 30
PROOF_TIMEOUT = 15


def resolve_destination(destination_hash):
    if not RNS.Transport.has_path(destination_hash):
        print("[Node A] Path ke Node B belum diketahui, mengirim path request...")
        RNS.Transport.request_path(destination_hash)
        deadline = time.time() + PATH_TIMEOUT
        while not RNS.Transport.has_path(destination_hash):
            if time.time() > deadline:
                print("[Node A] Gagal menemukan path ke Node B")
                sys.exit(1)
            time.sleep(0.1)

    print(f"[Node A] Path ditemukan, jumlah hop: {RNS.Transport.hops_to(destination_hash)}")

    # Public key Node B diperoleh dari announce yang sudah diterima
    identity_b = RNS.Identity.recall(destination_hash)
    destination_b = RNS.Destination(
        identity_b,
        RNS.Destination.OUT,
        RNS.Destination.SINGLE,
        APP_NAME,
        ASPECT,
    )
    print(f"[Node A] Destination Node B: {destination_b}")
    return destination_b


def send_message(destination_b, pesan):
    packet  = RNS.Packet(destination_b, pesan.encode("utf-8"))
    receipt = packet.send()
    print(f"[Node A] Mengirim pesan: \"{pesan}\"")

    receipt.set_timeout(PROOF_TIMEOUT)
    while receipt.status == RNS.PacketReceipt.SENT:
        time.sleep(0.1)

    if receipt.status == RNS.PacketReceipt.DELIVERED:
        rtt = receipt.get_rtt()
        print(f"[Node A] Pesan terkirim, bukti diterima dari Node B (RTT {rtt*1000:.1f} ms)")
    else:
        print("[Node A] Bukti penerimaan tidak diterima (timeout)")


def main():
    if len(sys.argv) < 2:
        print(f"Penggunaan: python3 {sys.argv[0]} <destination_hash_node_b> [\"isi pesan\"]")
        sys.exit(1)

    dest_len = (RNS.Reticulum.TRUNCATED_HASHLENGTH // 8) * 2
    hexhash  = sys.argv[1].strip("<>")
    if len(hexhash) != dest_len:
        print(f"Destination hash harus {dest_len} karakter heksadesimal")
        sys.exit(1)
    destination_hash = bytes.fromhex(hexhash)

    RNS.Reticulum(configdir=CONFIG_DIR)
    destination_b = resolve_destination(destination_hash)

    if len(sys.argv) >= 3:
        send_message(destination_b, " ".join(sys.argv[2:]))
        return

    print("[Node A] Ketik pesan lalu Enter (Ctrl+C untuk keluar)")
    try:
        while True:
            pesan = input("> ")
            if pesan:
                send_message(destination_b, pesan)
    except (KeyboardInterrupt, EOFError):
        print("\n[Node A] Selesai")


if __name__ == "__main__":
    main()

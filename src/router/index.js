import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import SplashView from '@/views/auth/SplashView.vue'

/**
 * meta:
 *  - guestOnly   : hanya untuk yang belum login (login, daftar, …)
 *  - requiresAuth + role ('Pemilik' | 'Penghuni') : dari route induk
 *  - tab         : tab BottomNav yang aktif
 *  - hideNav     : sembunyikan BottomNav (halaman form/detail)
 *  - title       : judul dokumen
 */
const guest = (path, name, component, title, extra = {}) => ({
  path,
  name,
  component,
  meta: { guestOnly: true, title },
  ...extra,
})

const page = (path, name, component, meta) => ({ path, name, component, meta })

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // ---------- Autentikasi ----------
    guest('/', 'splash', SplashView, null),
    guest('/masuk', 'login', () => import('@/views/auth/LoginView.vue'), 'Masuk'),
    guest('/daftar', 'register', () => import('@/views/auth/RegisterView.vue'), 'Daftar Akun'),
    guest('/lupa-sandi', 'forgot-password', () => import('@/views/auth/ForgotPasswordView.vue'), 'Lupa Kata Sandi'),
    guest('/lupa-sandi/terkirim', 'forgot-password-sent', () => import('@/views/auth/ForgotPasswordSentView.vue'), 'Periksa Email', {
      beforeEnter: (to) => (to.query.email ? true : { name: 'forgot-password' }),
    }),
    {
      path: '/pengaturan-server',
      name: 'server-settings',
      component: () => import('@/views/auth/ServerSettingsView.vue'),
      meta: { title: 'Pengaturan Server' },
    },

    // ---------- Pemilik Kos ----------
    {
      path: '/pemilik',
      component: () => import('@/components/layout/PemilikLayout.vue'),
      meta: { requiresAuth: true, role: 'Pemilik' },
      children: [
        page('', 'pemilik-beranda', () => import('@/views/pemilik/DasborView.vue'), { tab: 'dasbor', title: 'Dasbor' }),
        page('keuangan', 'pemilik-keuangan', () => import('@/views/pemilik/KeuanganView.vue'), { tab: 'keuangan', title: 'Keuangan' }),
        page('keuangan/tagihan/:id', 'pemilik-tagihan-detail', () => import('@/views/pemilik/VerifikasiDetailView.vue'), { tab: 'keuangan', hideNav: true, title: 'Verifikasi Pembayaran' }),
        page('penghuni', 'pemilik-penghuni', () => import('@/views/pemilik/PenghuniListView.vue'), { tab: 'penghuni', title: 'Penghuni & Kamar' }),
        page('penghuni/tambah', 'pemilik-penghuni-tambah', () => import('@/views/pemilik/TambahPenghuniView.vue'), { tab: 'penghuni', hideNav: true, title: 'Tambah Penghuni' }),
        page('penghuni/:userId', 'pemilik-penghuni-detail', () => import('@/views/pemilik/PenghuniDetailView.vue'), { tab: 'penghuni', hideNav: true, title: 'Detail Penghuni' }),
        page('layanan', 'pemilik-layanan', () => import('@/views/pemilik/LayananView.vue'), { tab: 'layanan', title: 'Layanan' }),
        page('layanan/aspirasi/:id', 'pemilik-aspirasi-detail', () => import('@/views/pemilik/AspirasiDetailView.vue'), { tab: 'layanan', hideNav: true, title: 'Detail Aspirasi' }),
        page('layanan/barang-hilang/baru', 'pemilik-barang-hilang-baru', () => import('@/views/shared/BarangHilangFormView.vue'), { tab: 'layanan', hideNav: true, title: 'Buat Laporan Barang' }),
        page('lainnya', 'pemilik-lainnya', () => import('@/views/pemilik/LainnyaView.vue'), { tab: 'lainnya', title: 'Lainnya' }),
        page('pengumuman', 'pemilik-pengumuman', () => import('@/views/pemilik/PengumumanView.vue'), { tab: 'lainnya', hideNav: true, title: 'Pengumuman' }),
        page('aturan', 'pemilik-aturan', () => import('@/views/pemilik/AturanView.vue'), { tab: 'lainnya', hideNav: true, title: 'Aturan Kos' }),
        page('penilaian', 'pemilik-penilaian', () => import('@/views/pemilik/PenilaianView.vue'), { tab: 'lainnya', hideNav: true, title: 'Penilaian' }),
        page('kamar', 'pemilik-kamar', () => import('@/views/pemilik/KamarView.vue'), { tab: 'lainnya', hideNav: true, title: 'Kamar & Tarif' }),
        page('profil-kos', 'pemilik-profil-kos', () => import('@/views/pemilik/ProfilKosView.vue'), { tab: 'lainnya', hideNav: true, title: 'Profil Kos' }),
        page('akun', 'pemilik-akun', () => import('@/views/shared/AkunView.vue'), { tab: 'lainnya', hideNav: true, title: 'Akun Saya' }),
      ],
    },

    // ---------- Penghuni Kos ----------
    {
      path: '/penghuni',
      component: () => import('@/components/layout/PenghuniLayout.vue'),
      meta: { requiresAuth: true, role: 'Penghuni' },
      children: [
        page('', 'penghuni-beranda', () => import('@/views/penghuni/BerandaView.vue'), { tab: 'beranda', title: 'Beranda' }),
        page('tagihan', 'penghuni-tagihan', () => import('@/views/penghuni/TagihanView.vue'), { tab: 'tagihan', title: 'Tagihan' }),
        page('tagihan/:id', 'penghuni-tagihan-detail', () => import('@/views/penghuni/TagihanDetailView.vue'), { tab: 'tagihan', hideNav: true, title: 'Rincian Tagihan' }),
        page('layanan', 'penghuni-layanan', () => import('@/views/penghuni/LayananView.vue'), { tab: 'layanan', title: 'Aspirasi & Izin' }),
        page('layanan/aspirasi/baru', 'penghuni-aspirasi-baru', () => import('@/views/penghuni/AspirasiFormView.vue'), { tab: 'layanan', hideNav: true, title: 'Buat Aspirasi' }),
        page('layanan/izin/baru', 'penghuni-izin-baru', () => import('@/views/penghuni/IzinFormView.vue'), { tab: 'layanan', hideNav: true, title: 'Ajukan Izin' }),
        page('barang-hilang', 'penghuni-barang-hilang', () => import('@/views/penghuni/BarangHilangView.vue'), { tab: 'barang', title: 'Barang Hilang' }),
        page('barang-hilang/baru', 'penghuni-barang-hilang-baru', () => import('@/views/shared/BarangHilangFormView.vue'), { tab: 'barang', hideNav: true, title: 'Buat Laporan Barang' }),
        page('info', 'penghuni-info', () => import('@/views/penghuni/InfoView.vue'), { tab: 'info', title: 'Info Kos' }),
        page('profil', 'penghuni-profil', () => import('@/views/shared/AkunView.vue'), { tab: 'beranda', hideNav: true, title: 'Profil Saya' }),
      ],
    },

    { path: '/:pathMatch(.*)*', redirect: { name: 'splash' } },
  ],
  scrollBehavior: (to, from, saved) => saved ?? { top: 0 },
})

// Routing berbasis peran: peran berasal dari akun yang login, bukan dipilih manual (sesuai SKPL).
router.beforeEach((to) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated) return { name: 'login' }
  if (to.meta.role && auth.role !== to.meta.role) return { name: auth.homeRoute }
  if (to.meta.guestOnly && auth.isAuthenticated) return { name: auth.homeRoute }
  return true
})

router.afterEach((to) => {
  useUiStore().closeAlert()
  document.title = to.meta.title ? `${to.meta.title} · Kostopia` : 'Kostopia'
})

export default router

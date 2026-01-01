import './globals.css';
import AppShell from '../components/AppShell';

export const metadata = {
  title: 'LegalAssist (LocalStorage)',
  description: 'LocalStorage demo build (no Base44)'
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}

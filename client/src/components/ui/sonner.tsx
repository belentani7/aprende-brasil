import { Toaster as Sonner, type ToasterProps } from "sonner";

/**
 * A plataforma tem um único tema (claro). Manter o Toaster explícito evita
 * depender de next-themes e de qualquer leitura do sistema para decidir cores.
 */
const Toaster = (props: ToasterProps) => (
  <Sonner
    theme="light"
    className="toaster group"
    position="bottom-center"
    richColors
    closeButton
    {...props}
  />
);

export { Toaster };

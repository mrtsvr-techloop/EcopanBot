import * as React from "react";
import { createRoot } from "react-dom/client";
import { ChakraProvider } from "@chakra-ui/react";
import { extendTheme, withDefaultColorScheme } from "@chakra-ui/react";
import { nanoid } from 'nanoid';
import PublicChatView from "./PublicChatView";

const linkedinTheme = extendTheme(
  withDefaultColorScheme({ colorScheme: "linkedin" })
);

class PublicChatUI {
  constructor({ wrapper }) {
    this.wrapper = wrapper;
    this.init();
  }

  init() {
    // Genera un ID di sessione o usa quello esistente
    const sessionID = localStorage.getItem('ecopanbot_session_id') || nanoid();
    localStorage.setItem('ecopanbot_session_id', sessionID);
    
    const root = createRoot(this.wrapper);
    root.render(
      <ChakraProvider theme={linkedinTheme}>
        <PublicChatView sessionID={sessionID} />
      </ChakraProvider>
    );
  }
}

frappe.provide("ecopanbot.public");
ecopanbot.public.PublicChatUI = PublicChatUI;
export default PublicChatUI;
Java cacerts file
=================

OpenSSL peut aider à tester un cacerts Java (fichier des certificats « de confiance »), ce qui peut être utile car aucun utilitaire n'existe pour cette tâche.

.. code-block:: bash
   :caption: Etape 0 : se préparer un répertoire de travail

   mkdir /tmp/cacerts-work
   cd /tmp/cacerts-work


.. code-block:: bash
   :caption: Etape 1 : récupérer le cacerts java. En l'absence de configuration plus précise (via javax.net.ssl.trustStore), le fichier est fourni par la JVM

   cp $JAVA_HOME/jre/lib/security/cacerts cacerts

.. code-block:: bash
   :caption: Etape 2 : convertir dans un format exploitable par OpenSSL? (changer le mot de passe par défaut si nécessaire)

   keytool -list -storepass changeit -keystore cacerts -rfc > cacerts.pem

.. code-block:: bash
   :caption: Etape 3a : valider le certificat, via les fichiers de certificat (pem + chaîne)

   # Valider un certificat fichier (cert.pem) avec sa chaîne (chain.pem, optionnel, fourni par SSLCertificateChainFile dans une conf Apache)
   openssl verify -untrusted chain.pem -CAfile cacerts.pem -CApath nopath cert.pem
   # ou (sans chaine)
   openssl verify -CAfile cacerts.pem -CApath nopath cert.pem
   # NOTA: -CApath nopath permet d'ignorer les certificats par défaut openssl en spécifiant un répertoire inconnu
   
   # Exemple de sortie si OK
   # cert.pem: OK
   
   # Exemple de sortie si KO
   # cert.pem: CN = projects.openwide.fr
   # error 20 at 0 depth lookup:unable to get local issuer certificate

.. code-block:: bash
   :caption: Etape 3b : valider par connexion à un serveur HTTPS

   # Valider un serveur (NOTA: openssl s_client devrait permettre de procéder à cette vérification
   # mais il prend toujours en compte les CA systèmes même avec -CApath nopath
   # on utilise gnutls-cli
   gnutls-cli --x509cafile cacerts.pem domain.com < /dev/null
   
   # Exemple de sortie si OK
   # [...] - Handshake was completed [...]
   
   # Exemple de sortie si KO
   # [...]
   # *** PKI verification of server certificate failed...
   # *** Fatal error: Error in the certificate.
   # *** Handshake has failed

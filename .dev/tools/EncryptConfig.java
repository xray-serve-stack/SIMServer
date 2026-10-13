import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.util.Base64;

public class EncryptConfig {

    private static final int IV_LENGTH = 12;
    private static final int TAG_LENGTH_BITS = 128;

    private static String bytesToHex(byte[] bytes) {
        return java.util.HexFormat.of().formatHex(bytes);
    }

    public static void main(String[] args) throws Exception {
        Path caPath = Path.of("certs", "ca", "ca.crt");
        Path inputPath = Path.of(".dev", "tools", "config.json");

        Path encryptedOutputPath =
                Path.of(".dev", "tools", "simserve_config.enc");

        Path base64OutputPath =
                Path.of(".dev", "tools", "simserve_config.b64");

        byte[] ca = Files.readAllBytes(caPath);
        byte[] plaintext = Files.readAllBytes(inputPath);

        MessageDigest sha256 = MessageDigest.getInstance("SHA-256");

        // AES-256 key = SHA-256(CA certificate)
        byte[] keyBytes = sha256.digest(ca);

        byte[] iv = new byte[IV_LENGTH];
        SecureRandom random = new SecureRandom();
        random.nextBytes(iv);

        SecretKeySpec key = new SecretKeySpec(keyBytes, "AES");

        GCMParameterSpec gcmSpec =
                new GCMParameterSpec(TAG_LENGTH_BITS, iv);

        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.ENCRYPT_MODE, key, gcmSpec);

        // Java GCM output = ciphertext || authentication tag
        byte[] ciphertextAndTag = cipher.doFinal(plaintext);

        // File format:
        // IV (12 bytes) || ciphertext || GCM tag
        byte[] output = new byte[iv.length + ciphertextAndTag.length];

        System.arraycopy(
                iv,
                0,
                output,
                0,
                iv.length
        );

        System.arraycopy(
                ciphertextAndTag,
                0,
                output,
                iv.length,
                ciphertextAndTag.length
        );

        // Write original binary encrypted file.
        Files.write(encryptedOutputPath, output);

        // Encode the exact same encrypted bytes as Base64.
        String base64 = Base64.getEncoder().encodeToString(output);

        // Base64 is ASCII text, so write it as UTF-8 text.
        Files.writeString(
                base64OutputPath,
                base64,
                StandardCharsets.US_ASCII
        );

        // Diagnostics
        System.out.println(
                "CA SHA-256: "
                        + bytesToHex(sha256.digest(ca))
        );

        System.out.println(
                "AES key SHA-256: "
                        + bytesToHex(sha256.digest(keyBytes))
        );

        System.out.println(
                "simserve_config.enc SHA-256: "
                        + bytesToHex(
                                MessageDigest
                                        .getInstance("SHA-256")
                                        .digest(output)
                        )
        );

        System.out.println(
                "Base64 SHA-256: "
                        + bytesToHex(
                                MessageDigest
                                        .getInstance("SHA-256")
                                        .digest(
                                                base64.getBytes(
                                                        StandardCharsets.US_ASCII
                                                )
                                        )
                        )
        );

        System.out.println(
                "Encrypted: " + encryptedOutputPath
        );

        System.out.println(
                "Base64: " + base64OutputPath
        );

        System.out.println(
                "Plaintext size: "
                        + plaintext.length
                        + " bytes"
        );

        System.out.println(
                "Encrypted size: "
                        + output.length
                        + " bytes"
        );

        System.out.println(
                "Base64 size: "
                        + base64.length()
                        + " characters"
        );
    }
}
